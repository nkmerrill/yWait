from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .helpers import drawGraph, formatTime


from datetime import datetime

from .models import ComparisonSet, Location

# Create your views here.
def index(request):
  comparisonList = ComparisonSet.objects.order_by('-name')
  locationList = Location.objects.order_by('-venueName')
  context = {
    'comparisonList' : comparisonList,
    'locationList' : locationList,
    'permAddLoc' : request.user.has_perm('yWait.add_location'),
    'permAddComp' : request.user.has_perm('yWait.add_comparisonset'),
    'permViewLoc': request.user.has_perm('yWait.view_location'),
    'permViewComp': request.user.has_perm('yWait.view_comparisonset'),
  }

  if 'errorMSG' in request.session.keys():
    context['errorMSG'] = request.session['errorMSG']
    del request.session['errorMSG']
  
  return render(request, 'yWait/index.html', context)


class LocationView(LoginRequiredMixin, generic.DetailView):
  model = Location
  template_name = 'yWait/location/location.html'

  def get_context_data(self, *args, **kwargs):
    context = super(LocationView,self).get_context_data(*args, **kwargs)
    data = super().get_object().data.jsonToData()

    if 'errorMSG' in self.request.session.keys():
      context['errorMSG'] = self.request.session['errorMSG']
      del self.request.session['errorMSG']

    context['hours'] = formatTime(data['hour'],data['closed'])

    context['time'] = datetime.fromtimestamp(super().get_object().data.jsonToData()['epoch'])
    context['graph'] = drawGraph(data)

    context['perm'] = self.request.user.has_perm('yWait.view_location') 
    context['permUpdate'] = self.request.user.has_perm('yWait.change_location')
    context['permDelete'] = self.request.user.has_perm('yWait.delete_location')
    context['isAuthor'] = self.request.user == super().get_object().author

    return context

class ComparisonView(LoginRequiredMixin, generic.DetailView):
  model = ComparisonSet
  template_name = 'yWait/comparison/comparison.html'

  def get_context_data(self, *args, **kwargs):
    context = super(ComparisonView,self).get_context_data(*args, **kwargs)

    locationList = super().get_object().locations.all()

    data = super().get_object().data.jsonToData()

    if 'errorMSG' in self.request.session.keys():
      context['errorMSG'] = self.request.session['errorMSG']
      del self.request.session['errorMSG']

    context['address'] = data['address'] 
    context['name'] = data['name']

    context['time'] = datetime.fromtimestamp(super().get_object().data.jsonToData()['epoch'])

    context['hours'] = formatTime(data['hour'],data['closed'])
    
    context['locationList'] = locationList
    context['graph'] = drawGraph(data)

    context['perm'] = self.request.user.has_perm('yWait.view_comparisonset')
    context['permViewLoc'] = self.request.user.has_perm('yWait.view_location')
    context['permUpdate'] = self.request.user.has_perm('yWait.change_comparisonset')
    context['permDelete'] = self.request.user.has_perm('yWait.delete_comparisonset') 
    context['isAuthor'] = self.request.user == super().get_object().author

    return context


class LocationCreate(LoginRequiredMixin, generic.CreateView):
  model = Location
  template_name = 'yWait/location/locationCreate.html'
  fields = ['venueName', 'venueAddress']
  
  def form_valid(self, form):
    form.instance.author = self.request.user
    return super().form_valid(form)

  def get_success_url(self):
    return reverse('yWait:viewLocation', args=(self.object.pk,))

  def get_context_data(self, *args, **kwargs):
    context = super(LocationCreate,self).get_context_data(*args, **kwargs)

    context['perm'] = self.request.user.has_perm('yWait.add_location')
    return context

class ComparisonCreate(LoginRequiredMixin, generic.CreateView):
  model = ComparisonSet
  template_name = 'yWait/comparison/comparisonCreate.html'
  fields = ['name', 'locations']

  def form_valid(self, form):
    form.instance.author = self.request.user
    return super().form_valid(form)

  def get_success_url(self):
    self.object.updateData()
    return reverse('yWait:viewComparison', args=(self.object.pk,))

  def get_context_data(self, *args, **kwargs):
    context = super(ComparisonCreate,self).get_context_data(*args, **kwargs)
    context['perm'] = self.request.user.has_perm('yWait.add_comparisonset')
    return context

class LocationDelete(LoginRequiredMixin, generic.DeleteView):
  model = Location
  
  template_name = 'yWait/delete.html'

  def get_success_url(self):
    return reverse('yWait:index')

  def get_context_data(self, *args, **kwargs):
    context = super(LocationDelete,self).get_context_data(*args, **kwargs)
    context['perm'] = self.request.user.has_perm('yWait.delete_location') or self.request.user == super().get_object().author
    return context

class ComparisonDelete(LoginRequiredMixin, generic.DeleteView):
  model = ComparisonSet

  template_name = 'yWait/delete.html'

  def get_success_url(self):
    return reverse('yWait:index')

  def get_context_data(self, *args, **kwargs):
    context = super(ComparisonDelete,self).get_context_data(*args, **kwargs)
    context['perm'] = self.request.user.has_perm('yWait.delete_comparisonset') or self.request.user == super().get_object().author
    return context

class ComparisonModify(LoginRequiredMixin, generic.UpdateView):
  model = ComparisonSet
  fields = ["name","locations"]
  template_name = "yWait/comparison/comparisonMod.html"
  
  def get_success_url(self):
    return reverse('yWait:updateComparison', args=(self.object.pk,))
  
  def get_context_data(self, *args, **kwargs):
    context = super(ComparisonModify, self).get_context_data(*args, **kwargs)
    context['perm'] = self.request.user == super().get_object().author
    return context



@login_required()
@permission_required('yWait.change_location')
def updatelocation(request, pk):
  loc = Location.objects.get(pk = pk)
  #Make sure data is at least a week old before allowing an update
  #if datetime.fromtimestamp(loc.data.jsonToData()['epoch'])+timedelta(days=7) <= datetime.now():
  loc.save()
  #else:
    #request.session['errorMSG'] = "Data too fresh to update."
  
  return redirect(reverse('yWait:viewLocation', args=(pk,)))

@login_required()
@permission_required('yWait.change_comparisonset')
def updateComparison(request, pk):
  comp = ComparisonSet.objects.get(pk = pk)

  comp.updateData()
  locationList = comp.locations.all()
  if len(locationList) == 0:
    comp.delete()
    request.session['errorMSG'] = 'Comparison was empty and automatically deleted.'
    return redirect('yWait:index')
  else:
    return redirect(reverse('yWait:viewComparison', args=(pk,)))

def dashboard(request):
  template = 'yWait/users/dashboard.html'
  return render(request, template)