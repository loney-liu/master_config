# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook which chooses an environment file to use based on the current context.
"""

from tank import Hook


class PickEnvironment(Hook):
    def execute(self, context, **kwargs):
        """
        The default implementation assumes there are three environments, called shot, asset
        and project, and switches to these based on entity type.
        """
        if context.source_entity:
            if context.source_entity["type"] == "Version":
                return "version"
            elif context.source_entity["type"] == "PublishedFile":
                return "publishedfile"
            elif context.source_entity["type"] == "Playlist":
                return "playlist"

        if context.project is None:
            # Our context is completely empty. We're going into the site context.
            return "site"

        if context.entity is None:
            # We have a project but not an entity.
            return "project"

# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook which chooses an environment file to use based on the current context.
This file is almost always overridden by a configuration.
"""

from tank import Hook


class PickEnvironment(Hook):
    def execute(self, context, **kwargs):
        """
        Executed when Toolkit needs to pick an environment file.

        The default implementation will return ``shot`` or ``asset`` based
        on the type of the entity in :attr:`sgtk.Context.entity`. If the type
        does not match ``Shot`` or ``Asset``, ``None`` will be returned.

        :params context: The context for which an environment will be picked.
        :type context: :class:`~sgtk.Context`

        :returns: Name of the environment to use or ``None`` is there was no match.
        :rtype: str
        """
        # Must have an entity
        if context.entity is None:
            return None

        if context.entity["type"] == "Shot":
            return "shot"
        elif context.entity["type"] == "Asset":
            return "asset"

        return None

        if context.entity and context.step is None:
            # We have an entity but no step.
            if context.entity["type"] == "Shot":
                return "shot"
            if context.entity["type"] == "Asset":
                return "asset"
            if context.entity["type"] == "Sequence":
                return "sequence"
            if context.entity["type"] == "Episode":
                return "episode" 
            if context.entity["type"] == "CustomEntity01": 
                return "material"

        if context.entity and context.step:
            # We have a step and an entity.
            if context.entity["type"] == "Shot":
                return "shot_step"
            if context.entity["type"] == "Asset":
                return "asset_step"
            if context.entity["type"] == "CustomEntity01":
                return "material_step"

        return None
