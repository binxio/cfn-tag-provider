import os
import logging
import tag_provider


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def handler(request, context):
    return tag_provider.handler(request, context)
