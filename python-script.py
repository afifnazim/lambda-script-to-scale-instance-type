import boto3
import json
import time
import os
import logging

##### List provided by user, You can list can be of only 2 instance type or this long #####

li = ['t2.micro','t2.nano','t2.small','t2.large','t2.xlarge','t3.xlarge']

#################################


def StopEc2 (ec2,instance_id,logger):
    print('entered in StopEc2')
    #StopEc2
    ec2.stop_instances(InstanceIds=[instance_id]);
    stopped =1;
    waiter1=ec2.get_waiter('instance_stopped');
    waiter1.wait(InstanceIds=[instance_id],WaiterConfig={'Delay': 40,'MaxAttempts': 40});
    logger.info("Instance  Stopped.");
    print ("Stopped :  %s", instance_id);
    return 1

def StartEc2(ec2,instance_id,logger) :
    print('entered in StartEc2')
    #StartEc2
    logger.info("Starting Instance ");                         
    responses = ec2.start_instances(InstanceIds=[instance_id]);
    waiter2=ec2.get_waiter('instance_running');
    waiter2.wait(InstanceIds=[instance_id],WaiterConfig={'Delay': 40,'MaxAttempts': 40});
    logger.info("Instance  Started.");
    print ("Started :  %s", instance_id);
    return 1

def ReregisteredInELB(elb,instance_id,logger):
    print('entered in ReregisteredInELB')
    #regsiteragaintoElb and bring TargetInService
    response1 = elb.register_targets(
         TargetGroupArn='arn:aws:elasticloadbalancing:us-east-1:457709xxxxxx:targetgroup/xxxxxx/xxxxxx',      ##### TargetGroupArn provided by user #####
         Targets=[{'Id': instance_id,'Port': 80}]                                                             ##### Port provided by user #####
    );
    waiter3 = elb.get_waiter('target_in_service')
    waiter3.wait(
         TargetGroupArn='arn:aws:elasticloadbalancing:us-east-1:457709xxxxxx:targetgroup/xxxxxx/xxxxxx',      ##### TargetGroupArn provided by user #####
         Targets=[{'Id': instance_id,'Port': 80}]                                                             ##### Port provided by user #####
    ); 
    print(instance_id, " is Registered with ELB");
    return 1    
    
def deregisteredfromELB(elb,instance_id,logger):
    print('entered in deregisteredfromELB')
    response1 = elb.deregister_targets(
        TargetGroupArn='arn:aws:elasticloadbalancing:us-east-1:457709xxxxxx:targetgroup/xxxxxx/xxxxxx',       ##### TargetGroupArn provided by user #####
        Targets=[{'Id': instance_id ,'Port': 80}]                                                             ##### Port provided by user #####
    );
    waiter0=elb.get_waiter('target_deregistered');
    waiter0.wait(
        TargetGroupArn='arn:aws:elasticloadbalancing:us-east-1:457709xxxxxx:targetgroup/xxxxxx/xxxxxx',       ##### TargetGroupArn provided by user #####
        Targets=[{'Id': instance_id ,'Port': 80}]                                                             ##### Port provided by user #####
    );               
    print(instance_id, " is DeRegistered with ELB");
    return 1
    
def upgrade(ec2,instance_type,instance_id,logger,nexttype):
    print('entered in upgrade')
    ec2.modify_instance_attribute(InstanceId=instance_id, Attribute='instanceType', Value=nexttype);  ##### nexttype chose next instance type in sequence up #####
    print (instance_id, " resized");
    logger.info("Starting Instance ");                
    return 1 
        
def downgrade(ec2,instance_type,instance_id,logger,nextelem):
    print('entered in downgrade')
    ec2.modify_instance_attribute(InstanceId=instance_id,Attribute='instanceType',Value=nextelem);    ##### nextelem chose next instance type in sequence down#####
    print (instance_id, " resized");
    logger.info("Starting Instance ");                
    return 1 
    
 
##### Main Function #####

def lambda_handler(event, context):
 
    region = event['region']
    ec2 = boto3.client('ec2', region_name=region)
    elb = boto3.client('elbv2')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    stopped=0;
    logger.info("Event Object");
    logger.info(json.dumps(event));

    instance_id = event['detail']['configuration']['metrics'][0]['metricStat']['metric']['dimensions']['InstanceId'];
    print(type(instance_id));
    logger.info("Instance Id : %s", instance_id);

    ec2 = boto3.client('ec2', region);
    response = ec2.describe_instance_status(InstanceIds=[instance_id]);
    print(response)
    logger.info("Instance Detail");
    print(logger.info(json. dumps(response)));

    ########################################
    ## CheckEc2type, state, alarm state ###
    ########################################
    response2= ec2.describe_instance_attribute(Attribute='instanceType',InstanceId=instance_id);
    print(response2)
    instance_type = response2['InstanceType']['Value'];
    print(instance_type, 'this is existing instance type of', instance_id )

    instance_state = response['InstanceStatuses'][0]['InstanceState']['Name'];
    logger.info("Instance State : %s", instance_state);
    
    Alarmstate = event['detail']['state']['value'];
    print( 'Alarm State: ', Alarmstate )
      
    AlarmName = event['detail']['alarmName']
    print('Alarm Name: ', AlarmName )
    
    #########################################################
    # For Upgrade - checking next available in sequence #####
    #########################################################
        
    for currenttype in li:
        if (li.index(currenttype))+1 != len(li):
            if instance_type == currenttype:
                nexttype = li[li.index(currenttype)+1]
                print ('This is next upgradable InstanceType available in given list sequence =',nexttype )
                break
        else:
            pass

    ################################################################
    ## For Downgrade - this will automatically reverse the sequence##
    ################################################################

    print("List before reverse : ",li)
    Rev_li = []
    for value in li:
        i = 0
        Rev_li.insert(i,value)
        i+1
    print("List after reverse : ", Rev_li)

    

    #############################################################
    # For Downgrade - checking next available in sequence ######
    ############################################################
    
    for elem in Rev_li:
        if instance_type == elem:
            nextelem = Rev_li[Rev_li.index(elem)+1]
            print ('This is next downgradable InstanceType available in given list sequence =',nextelem )
            break
        else:
            pass

    ############################################
    ###### This is Main Logic of the Code  #####
    ############################################
    
    try :
        
        if instance_state == 'running':
            ### do the resize if instance is running , no for stopped instance
            if instance_type != 't3.xlarge' and Alarmstate == 'ALARM':     #### 't3.xlarge'  is a manual entry provided by user , replace as per requirement but ensure it should be top from list
                print('deregisteredfromELB in progress')
                deregisteredfromELB(elb,instance_id,logger)
                print('deregisteredfromELB is completed')
                print('StopEc2 in progress')
                StopEc2 (ec2,instance_id,logger)   
                print('StopEc2 is completed')
                print('upgrade in progress')
                upgrade(ec2,instance_type,instance_id,logger,nexttype)
                print('upgrade is completed')
                StartEc2(ec2,instance_id,logger) 
                print('ReregisteredInELB in progress')
                ReregisteredInELB(elb,instance_id,logger)
                print('ReregisteredInELB in completed')
                print('upgrade done')
                
            elif instance_type != 't2.micro' and Alarmstate == 'OK':        #### 't2.micro' is a manual entry provided by user , replace as per requirement but ensure it should be basic from list
                print('deregisteredfromELB in progress')
                deregisteredfromELB(elb,instance_id,logger)
                print('deregisteredfromELB is completed')
                print('StopEc2 in progress')
                StopEc2 (ec2,instance_id,logger)   
                print('StopEc2 is completed')
                print('downgrade in progress')
                downgrade(ec2,instance_type,instance_id,logger,nextelem)
                print('downgrade is completed')
                StartEc2(ec2,instance_id,logger) 
                print('ReregisteredInELB in progress')
                ReregisteredInELB(elb,instance_id,logger)
                print('ReregisteredInELB in completed')
                print('Downgrade done')
            else:
                print('Not matching any conditions for upgrade or downgrade')
        else:
            logger.info("Instance already running lowest or highest instance type");
            raise
    except IndexError as e:
        print(e)
        logger.info("Instance state Not available or Not running");
        return 0;  
    except :
        print('This is impossible condition - alarm can not trigger without having datapoints of running instance but as a backup case scenario')
    return 1;
