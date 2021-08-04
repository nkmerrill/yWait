TEST = False #WARNING: Seeing to False will use LIVE DATA that can incur a cost! Please only set to False when live data tests are needed! For testing data, edit the values in sampleresponse.json instead!
TESTRESPONSE = "yWait/sampleresponse.json"

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
import json, os, requests




#Data object
class pureData():
  def __init__(self):
    self.data = { 
      'epoch':0, 
      'hour': [[],[],[],[],[],[],[]],
      'closed':[True,False,False,False,False,False,True],
      'address':['','','','','','',''],
      'name':['','','','','','','']
       }

#Actual data from API regarding location traffic.
class trafficData(models.Model):

  jsonData = models.TextField(default = '')

  def jsonToData(self):
    output = json.loads(self.jsonData)
    return output

  def __str__(self):
    return str(self.pk) + ' trafficData'

#A location object
class Location(models.Model):
  #Name of venue passed to API (also user friendly name)
  venueName = models.CharField(max_length=256, unique=True)
  #Address of venue passed to API
  venueAddress = models.TextField()

  author = models.ForeignKey(User, on_delete=models.CASCADE)

  #Traffic data for this venue
  data = models.ForeignKey(trafficData, on_delete = models.SET_NULL, null=True, blank=True)
  
  def updateData(self):
    outData = pureData()
    if TEST == False:
      #call API and gather data  
      apiKey = os.environ['APIKEY']
      url = "https://besttime.app/api/v1/forecasts"
      params = {
        'api_key_private' : apiKey,
        'venue_name': self.venueName,
        'venue_address' : self.venueAddress 
      }

      responseData = requests.request("POST",url, params=params).text
      unParsed = json.loads(responseData)

      #To ensure API usage is consistent with expectations, address will be pulled from API
      self.venueAddress = unParsed["venue_info"]["venue_address"]

    else:
      #TEST RESPONSE#
      responseData = ""
      with open(TESTRESPONSE, "r") as f:
        responseData = f.read()

      #parse API data for needed information  
      unParsed = json.loads(responseData)
          
    outData.data['epoch'] = int(unParsed["epoch_analysis"])

    for i in range(7): #API response is broken down as a list of days.
      outData.data['address'][i] = self.venueAddress
      outData.data['name'][i] = self.venueName

      if unParsed['analysis'][i]['day_info']['venue_open'] == 'Closed':
        outData.data['closed'][i] = True
      else:
        outData.data['hour'][i] = unParsed['analysis'][i]['quiet_hours']
        outData.data['closed'][i] = False

    #Delete old data, if it exists
    if self.data is not None:
      trafficData.objects.get(pk=self.data.pk).delete()

    #create trafficData using parsed information and assign it to the object.
    trafData = trafficData(jsonData = json.dumps(outData.data))
    trafData.save()
    self.data = trafData

  def __str__(self):
    return self.venueName


#Set of locations to be compared.
class ComparisonSet(models.Model):
  name = models.CharField(max_length=200, unique=True)
  author = models.ForeignKey(User, on_delete=models.CASCADE)

  #Traffic data for this comaprison set
  data = models.ForeignKey(trafficData, on_delete= models.SET_NULL, null=True, blank=True)

  #Comparisons for the Location objects
  locations = models.ManyToManyField(Location, related_name='compLocations')

  def updateData(self):
    outData = pureData()

    for i in range(7):
      smallestCount = 0
      smallestLocData = None
      for locale in self.locations.all():
        locData = locale.data.jsonToData()
        if len(locData['hour'][i]) >= smallestCount and not locData['closed'][i] :
          smallestCount = len(locData['hour'][i])
          smallestLocData = locData
      if smallestLocData is None:
        outData.data['hour'][i] = []
        outData.data['closed'][i] = True
        outData.data['address'][i] = '-'
        outData.data['name'][i] = '-'
      else:
        outData.data['hour'][i] = smallestLocData['hour'][i]
        outData.data['closed'][i] = smallestLocData['closed'][i]
        outData.data['address'][i] = smallestLocData['address'][i]
        outData.data['name'][i] = smallestLocData['name'][i]

    outData.data['epoch'] = datetime.now().timestamp()
    
    #Data old data, if it exists
    if self.data is not None:
      trafficData.objects.get(pk=self.data.pk).delete()

    #Create trafficData using information found  
    trafData = trafficData(jsonData = json.dumps(outData.data))
    trafData.save()
    self.data = trafData
    self.save()
  
  def __str__(self):
    return self.name
  


@receiver(pre_delete,sender=Location, dispatch_uid="delete data Location")
@receiver(pre_delete,sender=ComparisonSet, dispatch_uid="delete data ComparisonSet")
def deleteDataSignal(sender,instance,using,**kwargs):
  data = trafficData.objects.get(pk=instance.data.pk)
  data.delete()

@receiver(pre_save, sender=Location, dispatch_uid="save data Location")
def updateDataSignal(sender, instance, using, **kwargs):
  instance.updateData()

