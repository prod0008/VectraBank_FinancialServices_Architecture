# infrastructure/deploy_stack.py
import boto3
import os

STACK_NAME = "lesson-10-exercise-support"

def main():
    print(f"🔍 Checking for CloudFormation stack: {STACK_NAME}...")
    cf = boto3.client('cloudformation')
    
    try:
        response = cf.describe_stacks(StackName=STACK_NAME)
        stack = response['Stacks'][0]
        print(f"✅ Found stack! Status: {stack['StackStatus']}")
        
        if stack['StackStatus'] == 'CREATE_COMPLETE':
            print("\n📦 Discovered Resource Outputs:")
            env_updates = {}
            for output in stack.get('Outputs', []):
                print(f"   {output['OutputKey']}: {output['OutputValue']}")
                env_updates[output['OutputKey']] = output['OutputValue']
            
            # Append/Update .env file with real IDs
            env_file = '.env'
            existing_vars = {}
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if '=' in line:
                            k, v = line.strip().split('=', 1)
                            existing_vars[k] = v
            
            existing_vars.update(env_updates)
            
            with open(env_file, 'w') as f:
                for k, v in existing_vars.items():
                    f.write(f"{k}={v}\n")
                    
            print(f"\n✅ Successfully updated .env with real resource IDs!")
            print("Next step: Ensure vectrabank_architecture.py uses os.getenv() to read these, then run it.")
        else:
            print(f"⚠️ Stack is still deploying (Status: {stack['StackStatus']}). Please wait 2-3 minutes and run this script again.")
            
    except cf.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            print(f"❌ Stack '{STACK_NAME}' does not exist in this AWS account.")
            print("\n💡 Action Required:")
            print("1. The Udacity workspace usually pre-deploys this stack, or provides a template.yaml.")
            print("2. If you have template.yaml, run: aws cloudformation deploy --template-file infrastructure/template.yaml --stack-name lesson-10-exercise-support --capabilities CAPABILITY_NAMED_IAM")
            print("3. If not, you can use placeholder IDs in your .env file to complete the architecture exercise locally.")
        else:
            print(f"AWS Error: {e}")

if __name__ == "__main__":
    main()
