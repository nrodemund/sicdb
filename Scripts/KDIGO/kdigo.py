# This script example documents the algorithm of the KDIGO_AKI_168 field.
# Note that the urine output method may overestimate kidne injury


import sys
import matplotlib.pyplot as plt
from random import random
import os

rds_path=os.path.dirname(__file__)+r"\..\RooDataServer\RooDataServer\Python"
sys.path.append(rds_path)

import RooDataServer

roodata=RooDataServer.RooDataServer()
roodata.Connect()
sicdb=roodata.LoadDataset("sicdb")
targetcur=sicdb.cursor() # this is a default python mysql cursor

def GetValue(query,param=None,nullvalue=None):
    global targetcur
    targetcur.execute(query,param)
    ret=targetcur.fetchone()  
    return ret[0] if ret is not None else nullvalue

# --- Set metadata ---

creatinine_id = 367
observation_hours=168  # time of observation
target_var_name="KDIGO_AKI_168" # target field name
target_id =sicdb.GetRefID("ProcessedFields",target_var_name,True) # creates a new reference if needed
target_id_only_crea =sicdb.GetRefID("ProcessedFields",target_var_name+"_OC",True)
aki_ids = [sicdb.GetRefID("KDIGO_AKI","0",True),
                    sicdb.GetRefID("KDIGO_AKI","1",True),
                    sicdb.GetRefID("KDIGO_AKI","2",True),
                    sicdb.GetRefID("KDIGO_AKI","3",True)]



# --- Fetch patient list ---
#targetcur.execute("SELECT caseid,WeightOnAdmission/1000,HeartSurgeryEndOffset,HeightOnAdmission FROM cases WHERE HeartSurgeryEndOffset >0")
targetcur.execute("SELECT caseid,WeightOnAdmission/1000,HeartSurgeryEndOffset,HeightOnAdmission FROM cases")

patients=targetcur.fetchall()


kdigo_stats_caseid={}
onlycrea=0
count_anuria=0
# --- Creatinine  ---
kdigocount = [0,0,0,0]
nocreacount=0
for patient in patients:
    kdigo=0
    weight=patient [1]
    caseid=patient [0]
    offsetbegin = 0
    offsetend=offsetbegin + (3600*observation_hours)
    creatinine_baseline = GetValue("SELECT LaboratoryValue FROM laboratory WHERE laboratoryid=367 AND caseid=%s AND offset>-86400 AND offset<%s ORDER BY offset ASC LIMIT 1",(caseid,offsetend))
    creatinine_max48 = GetValue("SELECT Max(LaboratoryValue) FROM laboratory WHERE laboratoryid=367 AND  caseid=%s AND offset>=%s and offset <%s GROUP BY caseid",(caseid,offsetbegin,offsetbegin+48*3600),0)
    creatinine_max = GetValue("SELECT Max(LaboratoryValue) FROM laboratory WHERE laboratoryid=367 AND  caseid=%s AND offset>=%s and offset <%s GROUP BY caseid",(caseid,offsetbegin,offsetend))
    crrt=GetValue("SELECT id FROM data_float_h WHERE dataid = 723 and caseid=%s AND offset>=%s and offset <%s LIMIT 1",(caseid,offsetbegin,offsetend))

    if crrt is not None:
        kdigo=3

    if creatinine_baseline is None or creatinine_max is None:
        nocreacount=nocreacount+1
    else:
        # Note: we ignore that in KDIGO definition there is no staging between 1.9 and <2.0 and changed it to >2
        if creatinine_max48 > (creatinine_baseline+0.3):kdigo=1
        if creatinine_max > (creatinine_baseline*1.5):kdigo=1
        if creatinine_max > (creatinine_baseline*2):kdigo=2
        if creatinine_max > (creatinine_baseline*3):kdigo=3
        if creatinine_max > 4 and (creatinine_max-creatinine_baseline)>0.5: kdigo=3            
    
    kdigocount[kdigo] = kdigocount[kdigo]+1
    kdigo_stats_caseid[caseid] = kdigo
print ("Step one finished. Skipped patients for no data: ", nocreacount)
print("creatinine",kdigocount)
plt.pie(kdigocount,labels=["0","1","2","3"])
plt.show()


def CalculateAverageInRange(hour_from, hour_to, values):
    if not hour_from in values or not hour_to in values: return 0,0,[]
    valsum=0
    count=0
    values_used=[]
    for i in range(hour_from,hour_to+1):
        if i in values:
            valsum+=values[i]
            count+=1
            values_used.append((i,values[i]))
    avg = valsum / (hour_to-hour_from+1)

    return avg,count,values_used

# --- Urine  ---
kdigo_urine_count = [0,0,0,0]
for patient in patients:
    kdigo=0
    weight=70 #patient [1]
    if weight == 0:weight=70
    caseid=patient [0]
    offsetbegin = 0#patient[2]
    offsetend=offsetbegin + (3600*observation_hours)
    targetcur.execute("SELECT floor(offset/3600),val FROM data_float_h WHERE caseid=%s and dataid=725 and offset>=%s and offset<%s ORDER BY offset ASC ",(caseid,offsetbegin,offsetend))
    hourly_values_raw = targetcur.fetchall()
    #hourly_values={x[0]: x[1] for x in hourly_values_raw }
    
    # KDIGO is a little bit unclear defined, as "more than 6 hours" is difficult to interprete. 
    
    # We have decided to use a moving average method, which calculates averages for every plausible timespan (i.e. 0-7, 1-8, 2-9, 3-10,...), 
    # as this meets the definition of KDIGO best.
    # Note: KDIGO defines <0.5/kg/h for >6h. As this definition is met with 7h, the selected timespan is 7h
    # Note: KDIGO does not define if output is <0.5/kg/h for >6h in average or absolutely, we use average
        
    if len(hourly_values_raw) ==0:continue # no data (this occurs if patient has no catheter)
    hourly_values={x[0]: x[1] for x in hourly_values_raw }
    
    offsetbegin_h=offsetbegin/3600
    observation_hour_offset=offsetbegin // 3600
    kdigo=0
    for i in range(offsetbegin,offsetend,3600):# loop for every hour in observation time
       hour =  (i // 3600)
       urine_sum=0
       urine_avg=0
       urine_count=0
       anuria=0
       if hour > 6+observation_hour_offset:
          urine_avg,urine_count,values_used = CalculateAverageInRange(hour-6,hour,hourly_values) # = average of last 7 hours
          
          if urine_avg / weight < 0.5 and urine_count>0 :kdigo=1
       if hour > 12+observation_hour_offset:
          # if hour-12 in hourly_values and hour-11 in hourly_values and hour-10 in hourly_values and hour-9 in hourly_values and hour-8 in hourly_values and hour-7 in hourly_values:
           
           if hour-12 in hourly_values and hour in hourly_values:

               
               urine_avg,urine_count,values_used = CalculateAverageInRange(hour-12,hour,hourly_values) 
               if urine_avg / weight < 0.5 and urine_count>0 :
                   kdigo=2
                   #if random()>0.97:print(values_used)
               if urine_avg==0 and urine_count>0:anuria=1
       if hour > 24+observation_hour_offset:
            if hour-24 in hourly_values and hour in hourly_values: 
               urine_avg,urine_count,values_used = CalculateAverageInRange(hour-24,hour,hourly_values) 

               if urine_avg / weight < 0.3 and urine_count>0 :kdigo=3             
    kdigo_urine_count[kdigo] = kdigo_urine_count[kdigo]+1
    if kdigo_stats_caseid[caseid]>kdigo:onlycrea+=1
    if kdigo_stats_caseid[caseid]<kdigo: kdigo_stats_caseid[caseid]=kdigo
    if anuria==1:count_anuria+=1
    
   
    
    
print("urine",kdigo_urine_count)
plt.pie(kdigo_urine_count,labels=["0","1","2","3"])
plt.show()   

# calculate sums for validation and plausibility check
combined = [0,0,0,0]
for kdigo in kdigo_stats_caseid.values():
    combined[kdigo] = combined[kdigo]+1

print("combined",combined)
plt.pie(combined,labels=["0","1","2","3"])
plt.show()   

print("OnlyCrea",onlycrea)
print("CountAnuria",count_anuria)




import unittest
class Validate(unittest.TestCase):
    def test_all_patients(self):
        global combined
        global patients
        self.assertEqual(sum(combined),len(patients),"Amount of patients != Sum")
    def test_all_over_0(self):
        global combined
        self.assertTrue(combined[0]>0 and combined[1]>0 and combined[2]>0 and combined[2]>0,"Not all kdigo classes found")
    def test_inplausible(self):
        global combined
        self.assertLess(combined[3], combined[0],"implausible:kdigo 3>kdigo 0")
unittest.main(exit=False)

# --- Update data ---
for patient in patients:
    caseid=patient[0]
    targetcur.execute("REPLACE INTO data_ref (CaseID,FieldID,RefID) VALUES (%s,%s,%s)",(caseid,target_id,aki_ids[kdigo_stats_caseid[caseid]]))
    
sicdb.commit() # commit transaction (autocommit is off on default)