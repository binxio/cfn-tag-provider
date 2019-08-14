import os
import json
import logging
import boto3
import requests
from cfn_resource_provider import ResourceProvider

log = logging.getLogger()
log.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

request_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "type": "object",
        "required": ["ResourceARN", "Tags"],
        "properties": {
            "ResourceARN": {"type": "string", "description": "of the resource"},
            "Tags": {"type": "object"},
        },
    },
}


class TagProvider(ResourceProvider):
    def __init__(self):
        super(TagProvider, self).__init__()
        self.rg_tagging = boto3.client("resourcegroupstaggingapi")

    @property
    def resource_arn(self):
        return self.get("ResourceARN")

    @property
    def old_resource_arn(self):
        return self.get_old("ResourceARN", self.resource_arn)

    @property
    def tags(self):
        return self.get("Tags")

    @property
    def old_tags(self):
        return self.get_old("Tags", self.tags)

    def has_changes(self):
        return self.resource_arn != self.old_resource_arn or self.tags != self.old_tags

    def check_errors(self, response):
        if response['FailedResourcesMap']:
            log.error('response %s', response)
            self.fail(response['FailedResourcesMap'][0].get('ErrorMessage'))
            return False
        return True

    def apply_tags(self):
        response = self.rg_tagging.tag_resources(
            ResourceARNList=[self.resource_arn], Tags=self.tags
        )
        self.check_errors(response)

    def create(self):
        self.apply_tags()
        self.physical_resource_id = self.logical_resource_id

    def update(self):
        if self.has_changes():
            self.delete_old()
            self.apply_tags()
        else:
            self.success("no changes")

    def delete_old(self):
        keys = list(self.old_tags.keys())
        if keys:
            response = self.rg_tagging.untag_resources(
                ResourceARNList=[self.resource_arn], TagKeys=keys
            )

    def delete(self):
        keys = list(self.tags.keys())
        if keys:
            response = self.rg_tagging.untag_resources(
                ResourceARNList=[self.resource_arn], TagKeys=keys
            )


provider = TagProvider()


def handler(request, context):
    return provider.handle(request, context)
