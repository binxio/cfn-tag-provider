# Custom::Tag
The `Custom::Tag` resource provider allows you to specify tags on any AWS resource.

## Syntax
To tag a resource using your your AWS CloudFormation template, use the following syntax:

```yaml
ResourceTag:
  Type: Custom::Tag
  Properties:
    ResourceARN: <ARN>
    Tags:
      <key>: <value>
    ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-tag-provider'
```

## Properties
You can specify the following properties:

- `ResourceARN`  - the ARN of the resource to tag.
- `Tags`  - dictionary of tags to apply.

## Return values
There are no return values. When referencing the resource, the logical resource id will be returned.

