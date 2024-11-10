# tag-provider
CloudFormation custom resource provider for managing any AWS resource tags. Sometimes a resource, such as AWS::EC2::EIP, does support
tags but not in CloudFormation. With the provider you can specify tags as a separate CloudFormation resource.

# How does it work?
Very simply, add a [Custom::Tag](docs/tag.md) to your CloudFormation template:

```yaml
EIPBastionPoolTag:
  Type: Custom::Tag
  Properties:
    ResourceARN:
      - !Sub 'arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:eip/${EIP1.AllocationId}'
      - !Sub 'arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:eip/${EIP2.AllocationId}'
      - !Sub 'arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:eip/${EIP3.AllocationId}'
    Tags:
      EIPPoolName: eip-bastion-pool

    ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-tag-provider'
```
You can tag any resource and add multiple tags in a single resource.

### Deploy the provider
To deploy the provider, type:

```sh
aws cloudformation create-stack \
        --capabilities CAPABILITY_IAM \
        --stack-name cfn-tag-provider \
        --template-body file://./cloudformation/cfn-resource-provider.yaml

aws cloudformation wait stack-create-complete  --stack-name cfn-tag-provider
```

This CloudFormation template will use our pre-packaged provider from `463637877380.dkr.ecr.eu-central-1.amazonaws.com/xebia/cfn-tag-provider:0.0.0`.


### Deploy the demo
In order to deploy the demo, type:

```sh
aws cloudformation create-stack \
        --capabilities CAPABILITY_NAMED_IAM \
        --stack-name cfn-tag-provider-demo \
        --template-body file://./cloudformation/demo.yaml

aws cloudformation wait stack-create-complete  --stack-name cfn-tag-provider-demo
```

## Permissions
The tag and untag resources operation requires query, tag and untag permissions on the tagged resources too. Currently, these IAM permissions are generated 
and added to the security policy of the provider using the script [add-allow-tag-actions-statement](bin/add-allow-tag-actions-statement). 

# Caveats
- untag commands fail silently.
