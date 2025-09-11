@echo off
echo 🚀 Deploying fixed task definition...

echo 📝 Registering new task definition...
aws ecs register-task-definition --cli-input-json file://task-definition.json --query "taskDefinition.taskDefinitionArn" --output text --region eu-north-1 > task-def-arn.txt
set /p TASK_DEF_ARN=<task-def-arn.txt
echo ✅ Task definition registered: %TASK_DEF_ARN%

echo 🔄 Updating ECS service...
aws ecs update-service --cluster HappyRobot-ECS --service shipments-taskdef-service-f8gz4zjz --task-definition %TASK_DEF_ARN% --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:eu-north-1:354918374652:targetgroup/APP-frontend/7a02fc7c09914764,containerName=frontend,containerPort=80 targetGroupArn=arn:aws:elasticloadbalancing:eu-north-1:354918374652:targetgroup/APP-backend/22b79997edea2035,containerName=backend,containerPort=8000 --region eu-north-1

echo ✅ Service updated

echo ⏳ Waiting for service to stabilize...
aws ecs wait services-stable --cluster HappyRobot-ECS --services shipments-taskdef-service-f8gz4zjz --region eu-north-1

echo ✅ Service is stable

echo 🔍 Checking target group health...
echo Frontend targets:
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:eu-north-1:354918374652:targetgroup/APP-frontend/7a02fc7c09914764 --query "TargetHealthDescriptions[].{Target:Target.Id,Port:Target.Port,Health:TargetHealth.State}" --output table --region eu-north-1

echo Backend targets:
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:eu-north-1:354918374652:targetgroup/APP-backend/22b79997edea2035 --query "TargetHealthDescriptions[].{Target:Target.Id,Port:Target.Port,Health:TargetHealth.State}" --output table --region eu-north-1

echo 🎉 Deployment complete!
del task-def-arn.txt
