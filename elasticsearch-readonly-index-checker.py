import requests 
import json
import sys
from elasticsearch import Elasticsearch



#Loop to check which node in cluster is the current master
ESMaster=''
masterIndex=0
while ESMaster == '' and masterIndex <= 2:
   ESMasterResponse=requests.get('http://prod-hq-logging-es-master20{}:9200/_cat/master?pretty&h=node'.format(masterIndex))
   ESMaster = ESMasterResponse.text.replace("\n","")
   masterIndex += 1
   print("Master is {}".format(ESMaster))


#Establish connection to ES master node
es = Elasticsearch("http://{}:9200".format(ESMaster))

#Search cluster for indices with non-null values for read-only block
openIndices_request=requests.get('http://{}:9200/_all/_settings/index.blocks.read_only_allow_delete*'.format(ESMaster))
openIndices_json=json.loads(openIndices_request.text)

#If any found with read-only block, list them
trueRoIndices = [x for x in openIndices_json if openIndices_json[x]['settings']['index']['blocks']['read_only_allow_delete'] == 'true']
falseRoIndices = [x for x in openIndices_json if openIndices_json[x]['settings']['index']['blocks']['read_only_allow_delete'] == 'false']


#If none found, report that and end
if len(trueRoIndices) == 0 and len (falseRoIndices) == 0:
   print("No indices detected with non-null values for read-only setting.")

#If one or more found, fix them and report
else:
   if len(trueRoIndices) > 0:
      print("{} read-only indices detected:".format(len(trueRoIndices)))
      print(trueRoIndices)
      for roIndex in trueRoIndices:
         es.indices.put_settings(index=roIndex, body={
         "index.blocks.read_only_allow_delete": None
         })
         print("Removing true read-only flag from {}".format(roIndex))
  
   if len(falseRoIndices) > 0:
      print("{} indices detected with read-only flag set to false instead of null:".format(len(falseRoIndices)))
      print(falseRoIndices)
      for roIndex in falseRoIndices:
         es.indices.put_settings(index=roIndex, body={
         "index.blocks.read_only_allow_delete": None
         })
         print("Removing false read-only flag from {}".format(roIndex))
   


    





