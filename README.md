# tag-provider
CloudFormation custom resource provider for managing any AWS resource tags. Sometimes a resource, such as AWS::EC2::EIP, does support
tags but not in CloudFormation. Sometimes, a custom provider does not support tags directly, as it is not part of the API call. With
the provider you can specify tags as a separate CloudFormation resource.

# How does it work?
Very simply, add a [Custom::Tag](docs/tag.md) to your CloudFormation template:

```yaml
Tag:
  Type: Custom::Tag
  Properties:
    ResourceARN: !Ref EIP
    Tags:
      key: value
```

### Deploy the provider
To deploy the provider, type:

```sh
aws cloudformation create-stack \
        --capabilities CAPABILITY_IAM \
        --stack-name cfn-tag-provider \
        --template-body file://./cloudformation/cfn-resource-provider.yaml

aws cloudformation wait stack-create-complete  --stack-name cfn-tag-provider
```

This CloudFormation template will use our pre-packaged provider from `s3://binxio-public/lambdas/cfn-tag-provider-0.1.1.zip`.


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
