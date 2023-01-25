# lambda-script-to-scale-instance-type

We can use this simple python script to scale up or down instance type in a target group in aws infrastructure. 

Our target is to automatically scale up and scale down aws instances when the CPU/RAM utilization hits a certain level. We will use CloudWatch for checking the CPU/RAM utilization. To trigger the lambda function we will use Eventbridge when CW goes to alarm state. 

Tasks will be divided in two parts - 

1. ScaleUp

2. ScaleDown

Procedure will follow the below roadmap - 

<b> 1. For scaling up: </b>

<i > EC2 CPU metric --->Alarm1 -->Eventbridge Rule 1--> Lambda -->Work flow  { DeregisteredfromELB --> EC2 Stop ----> Resize if 't2.micro' --> then  't2.nano' ----> Start. ----> RegisterToELB  } </i >

<b> 2. For scaling down: </b> 

<i > EC2 CPU metric --->Alarm2 -->Eventbridge Rule 2--> Lambda --> Work flow  { DeregisteredfromELB --> EC2 Stop ----> Resize  if 't2.nano' -->then  't2.micro' / ----> Start. ----> RegisterToELB } </i >

Thanks to AWS support team for the help
