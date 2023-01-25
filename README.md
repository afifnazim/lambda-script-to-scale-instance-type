# lambda-script-to-scale-instance-type
We can use this simple python script to scale up or down instance type in a target group in aws infrastructure. 

Our target is to automatically scale up and scale down aws instances when the CPU/RAM utilization hits a certain level. We will use CloudWatch for checking the CPU/RAM utilization. To trigger the lambda function we will use Eventbridge when CW goes to alarm state. 

Tasks will be divided in two parts - 

1. ScaleUp

2. ScaleDown

Procedure will follow the below roadmap - 

1. For scaling up: 



Thanks to AWS support team for the help
