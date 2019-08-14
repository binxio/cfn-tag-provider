import uuid, copy
import logging
import boto3
from provider import handler
from cfn import cfn, delete_all_resources
import pytest

logging.basicConfig(level=logging.INFO)

rg_tagging = boto3.client("resourcegroupstaggingapi")

def get_resources(tag_key, tag_value):
    response = rg_tagging.get_resources(TagFilters=[{"Key": tag_key, "Values": [tag_value] }])
    return list(map(lambda r: r["ResourceARN"], response["ResourceTagMappingList"]))

@pytest.fixture
def resource_arn():
    ssm = boto3.client("ssm")
    name = f"{uuid.uuid4()}"
    account = boto3.client("sts").get_caller_identity()["Account"]
    ssm.put_parameter(Name=name, Value=name, Type="String", Overwrite=True)
    yield f"arn:aws:ssm:eu-central-1:{account}:parameter/{name}"
    ssm.delete_parameter(Name=name)

def test_crud(resource_arn):
    try:
        key = "u{}".format(uuid.uuid4())
        value = "v{}".format(uuid.uuid4())
        request = Request("Create", resource_arn, {key: value})
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        physical_resource_id = response.get("PhysicalResourceId")
        assert physical_resource_id

        resources = get_resources(key, value)
        assert resource_arn in resources

        new_key = key + "-2"
        new_value = value + "-2"
        update_request = Request("Update", resource_arn, {new_key: new_value}, physical_resource_id=physical_resource_id)
        update_request["OldResourceProperties"] = request["ResourceProperties"]
        response = cfn(handler, update_request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert physical_resource_id == response.get("PhysicalResourceId")


        resources = get_resources(new_key, new_value)
        assert resource_arn in resources

        resources = get_resources(key, value)
        assert resource_arn not in resources

        update_request["OldResourceProperties"]["Tags"] = update_request["ResourceProperties"]["Tags"]
        update_request["ResourceProperties"]["Tags"] ={key: value, new_key: new_value}
        response = cfn(handler, update_request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert physical_resource_id == response.get("PhysicalResourceId")

        resources = get_resources(new_key, new_value)
        assert resource_arn in resources

        resources = get_resources(key, value)
        assert resource_arn in resources

        delete_request = copy.deepcopy(update_request)
        delete_request["RequestType"] = "Delete"
        response = cfn(handler, update_request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]

    finally:
        delete_all_resources(handler)





class Request(dict):
    def __init__(self, request_type, arn, tags, physical_resource_id=None):
        request_id = "request-%s" % uuid.uuid4()
        self.update(
            {
                "RequestType": request_type,
                "ResponseURL": "https://httpbin.org/put",
                "StackId": "arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid",
                "RequestId": request_id,
                "ResourceType": f"Custom::Tag",
                "LogicalResourceId": f"tag-{request_id}",
                "ResourceProperties": {"ResourceARN": arn, "Tags": tags},
            }
        )

        if physical_resource_id:
            self["PhysicalResourceId"] = physical_resource_id


