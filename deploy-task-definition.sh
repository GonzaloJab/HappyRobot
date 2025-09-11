#!/bin/bash

# Deploy the fixed task definition
set -euo pipefail

echo "🚀 Deploying fixed task definition..."

# Register the new task definition
echo "📝 Registering new task definition..."
TASK_DEF_ARN=$(aws ecs register-task-definition \
  --cli-input-json file://task-definition.json \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text \
  --region eu-north-1)

echo "✅ Task definition registered: $TASK_DEF_ARN"

# Update the service
echo "🔄 Updating ECS service..."
aws ecs update-service \
  --cluster HappyRobot-ECS \
  --service shipments-taskdef-service-f8gz4zjz \
  --task-definition $TASK_DEF_ARN \
  --load-balancers \
    targetGroupArn=arn:aws:elasticloadbalancing:eu-north-1:354918374652:targetgroup/APP-frontend/7a02fc7c09914764,containerName=frontend,containerPort=80 \
    targetGroupArn=arn:aws:elasticloadbalancing:eu-north-1:354918374652:targetgroup/APP-backend/22b79997edea2035,containerName=backend,containerPort=8000 \
  --region eu-north-1

echo "✅ Service updated"

# Wait for service to stabilize
echo "⏳ Waiting for service to stabilize..."
aws ecs wait services-stable \
  --cluster HappyRobot-ECS \
  --services shipments-taskdef-service-f8gz4zjz \
  --region eu-north-1

echo "✅ Service is stable"

# Check target group health
echo "🔍 Checking target group health..."
echo "Frontend targets:"
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:eu-north-1:354918374652:targetgroup/APP-frontend/7a02fc7c09914764 \
  --query 'TargetHealthDescriptions[].{Target:Target.Id,Port:Target.Port,Health:TargetHealth.State}' \
  --output table \
  --region eu-north-1

echo "Backend targets:"
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:eu-north-1:354918374652:targetgroup/APP-backend/22b79997edea2035 \
  --query 'TargetHealthDescriptions[].{Target:Target.Id,Port:Target.Port,Health:TargetHealth.State}' \
  --output table \
  --region eu-north-1

echo "🎉 Deployment complete!"
