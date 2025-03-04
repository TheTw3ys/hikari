# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021-present davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Special additional endpoints used by the REST API."""
from __future__ import annotations

__all__: typing.Sequence[str] = (
    "ButtonBuilder",
    "CommandBuilder",
    "SlashCommandBuilder",
    "ContextMenuCommandBuilder",
    "ComponentBuilder",
    "TypingIndicator",
    "GuildBuilder",
    "InteractionAutocompleteBuilder",
    "InteractionDeferredBuilder",
    "InteractionResponseBuilder",
    "InteractionMessageBuilder",
    "InteractiveButtonBuilder",
    "LinkButtonBuilder",
    "SelectMenuBuilder",
    "TextSelectMenuBuilder",
    "ChannelSelectMenuBuilder",
    "SelectOptionBuilder",
    "TextInputBuilder",
    "InteractionModalBuilder",
    "MessageActionRowBuilder",
    "ModalActionRowBuilder",
)

import abc
import typing

from hikari import undefined

if typing.TYPE_CHECKING:
    import types

    from typing_extensions import Self

    from hikari import channels
    from hikari import colors
    from hikari import commands
    from hikari import components as components_
    from hikari import embeds as embeds_
    from hikari import emojis
    from hikari import files
    from hikari import guilds
    from hikari import locales
    from hikari import messages
    from hikari import permissions as permissions_
    from hikari import snowflakes
    from hikari import users
    from hikari import voices
    from hikari.api import entity_factory as entity_factory_
    from hikari.api import rest as rest_api
    from hikari.interactions import base_interactions
    from hikari.internal import time

_SelectMenuBuilderT = typing.TypeVar("_SelectMenuBuilderT", bound="SelectMenuBuilder[typing.Any]")
_ContainerT = typing.TypeVar("_ContainerT")


class TypingIndicator(abc.ABC):
    """Result type of `hikari.api.rest.RESTClient.trigger_typing`.

    This is an object that can either be awaited like a coroutine to trigger
    the typing indicator once, or an async context manager to keep triggering
    the typing indicator repeatedly until the context finishes.

    .. note::
        This is a helper class that is used by `hikari.api.rest.RESTClient`.
        You should only ever need to use instances of this class that are
        produced by that API.
    """

    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    def __await__(self) -> typing.Generator[None, typing.Any, None]:
        ...

    @abc.abstractmethod
    async def __aenter__(self) -> None:
        ...

    @abc.abstractmethod
    async def __aexit__(
        self,
        exception_type: typing.Type[BaseException],
        exception: BaseException,
        exception_traceback: types.TracebackType,
    ) -> None:
        ...


class GuildBuilder(abc.ABC):
    """Result type of `hikari.api.rest.RESTClient.guild_builder`.

    This is used to create a guild in a tidy way using the HTTP API, since
    the logic behind creating a guild on an API level is somewhat confusing
    and detailed.

    .. note::
        If you call `add_role`, the default roles provided by Discord will
        be created. This also applies to the `add_` functions for
        text channels/voice channels/categories.

    .. note::
        Functions that return a `hikari.snowflakes.Snowflake` do
        **not** provide the final ID that the object will have once the
        API call is made. The returned IDs are only able to be used to
        re-reference particular objects while building the guild format
        to allow for the creation of channels within categories,
        and to provide permission overwrites.

    Examples
    --------
    Creating an empty guild:

    .. code-block:: python

        guild = await rest.guild_builder("My Server!").create()

    Creating a guild with an icon:

    .. code-block:: python

        from hikari.files import WebResourceStream

        guild_builder = rest.guild_builder("My Server!")
        guild_builder.icon = WebResourceStream("cat.png", "http://...")
        guild = await guild_builder.create()

    Adding roles to your guild:

    .. code-block:: python

        from hikari.permissions import Permissions

        guild_builder = rest.guild_builder("My Server!")

        everyone_role_id = guild_builder.add_role("@everyone")
        admin_role_id = guild_builder.add_role("Admins", permissions=Permissions.ADMINISTRATOR)

        await guild_builder.create()

    .. warning::
        The first role must always be the `@everyone` role.

    Adding a text channel to your guild:

    .. code-block:: python

        guild_builder = rest.guild_builder("My Server!")

        category_id = guild_builder.add_category("My safe place")
        channel_id = guild_builder.add_text_channel("general", parent_id=category_id)

        await guild_builder.create()
    """

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of the guild to create."""

    @property
    @abc.abstractmethod
    def default_message_notifications(self) -> undefined.UndefinedOr[guilds.GuildMessageNotificationsLevel]:
        """Default message notification level that can be overwritten.

        If not overridden, this will use the Discord default level.
        """

    @default_message_notifications.setter
    def default_message_notifications(
        self, default_message_notifications: undefined.UndefinedOr[guilds.GuildMessageNotificationsLevel], /
    ) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def explicit_content_filter_level(self) -> undefined.UndefinedOr[guilds.GuildExplicitContentFilterLevel]:
        """Explicit content filter level that can be overwritten.

        If not overridden, this will use the Discord default level.
        """

    @explicit_content_filter_level.setter
    def explicit_content_filter_level(
        self, explicit_content_filter_level: undefined.UndefinedOr[guilds.GuildExplicitContentFilterLevel], /
    ) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def icon(self) -> undefined.UndefinedOr[files.Resourceish]:
        """Guild icon to use that can be overwritten.

        If not overridden, the guild will not have an icon.
        """

    @icon.setter
    def icon(self, icon: undefined.UndefinedOr[files.Resourceish], /) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def verification_level(self) -> undefined.UndefinedOr[typing.Union[guilds.GuildVerificationLevel, int]]:
        """Verification level required to join the guild."""

    @verification_level.setter
    def verification_level(
        self, verification_level: undefined.UndefinedOr[typing.Union[guilds.GuildVerificationLevel, int]], /
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def create(self) -> guilds.RESTGuild:
        """Send the request to Discord to create the guild.

        The application user will be added to this guild as soon as it is
        created. All IDs that were provided when building this guild will
        become invalid and will be replaced with real IDs.

        Returns
        -------
        hikari.guilds.RESTGuild
            The created guild.

        Raises
        ------
        hikari.errors.BadRequestError
            If any values set in the guild builder are invalid.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are already in 10 guilds.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def add_role(
        self,
        name: str,
        /,
        *,
        permissions: undefined.UndefinedOr[permissions_.Permissions] = undefined.UNDEFINED,
        color: undefined.UndefinedOr[colors.Colorish] = undefined.UNDEFINED,
        colour: undefined.UndefinedOr[colors.Colorish] = undefined.UNDEFINED,
        hoist: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        mentionable: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
    ) -> snowflakes.Snowflake:
        """Create a role.

        .. warning::
            The first role you create must always be the `@everyone` role.

        Parameters
        ----------
        name : str
            The role's name.

        Other Parameters
        ----------------
        permissions : hikari.undefined.UndefinedOr[hikari.permissions.Permissions]
            If provided, the permissions for the role.
        color : hikari.undefined.UndefinedOr[hikari.colors.Colorish]
            If provided, the role's color.
        colour : hikari.undefined.UndefinedOr[hikari.colors.Colorish]
            An alias for `color`.
        hoist : hikari.undefined.UndefinedOr[bool]
            If provided, whether to hoist the role.
        mentionable : hikari.undefined.UndefinedOr[bool]
            If provided, whether to make the role mentionable.

        Returns
        -------
        hikari.snowflakes.Snowflake
            The dummy ID for this role that can be used temporarily to refer
            to this object while designing the guild layout.

            When the guild is created, this will be replaced with a different
            ID.

        Raises
        ------
        ValueError
            If you are defining the first role, but did not name it `@everyone`.
        TypeError
            If you specify both `color` and `colour` together or if you try to
            specify `color`, `colour`, `hoisted`, `mentionable` or `position` for
            the `@everyone` role.
        """

    @abc.abstractmethod
    def add_category(
        self,
        name: str,
        /,
        *,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Collection[channels.PermissionOverwrite]
        ] = undefined.UNDEFINED,
    ) -> snowflakes.Snowflake:
        """Create a category channel.

        Parameters
        ----------
        name : str
            The channels name. Must be between 2 and 1000 characters.

        Other Parameters
        ----------------
        position : hikari.undefined.UndefinedOr[int]
            If provided, the position of the category.
        permission_overwrites : hikari.undefined.UndefinedOr[typing.Sequence[hikari.channels.PermissionOverwrite]]
            If provided, the permission overwrites for the category.

        Returns
        -------
        hikari.snowflakes.Snowflake
            The dummy ID for this channel that can be used temporarily to refer
            to this object while designing the guild layout.

            When the guild is created, this will be replaced with a different
            ID.
        """

    @abc.abstractmethod
    def add_text_channel(
        self,
        name: str,
        /,
        *,
        parent_id: undefined.UndefinedOr[snowflakes.Snowflake] = undefined.UNDEFINED,
        topic: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        rate_limit_per_user: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Collection[channels.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        nsfw: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
    ) -> snowflakes.Snowflake:
        """Create a text channel.

        Parameters
        ----------
        name : str
            The channels name. Must be between 2 and 1000 characters.

        Other Parameters
        ----------------
        position : hikari.undefined.UndefinedOr[int]
            If provided, the position of the channel (relative to the
            category, if any).
        topic : hikari.undefined.UndefinedOr[str]
            If provided, the channels topic. Maximum 1024 characters.
        nsfw : hikari.undefined.UndefinedOr[bool]
            If provided, whether to mark the channel as NSFW.
        rate_limit_per_user : hikari.undefined.UndefinedOr[int]
            If provided, the amount of seconds a user has to wait
            before being able to send another message in the channel.
            Maximum 21600 seconds.
        permission_overwrites : hikari.undefined.UndefinedOr[typing.Sequence[hikari.channels.PermissionOverwrite]]
            If provided, the permission overwrites for the channel.
        parent_id : hikari.undefined.UndefinedOr[hikari.snowflakes.Snowflake]
            The ID of the category to create the channel under.

        Returns
        -------
        hikari.snowflakes.Snowflake
            The dummy ID for this channel that can be used temporarily to refer
            to this object while designing the guild layout.

            When the guild is created, this will be replaced with a different
            ID.
        """

    @abc.abstractmethod
    def add_voice_channel(
        self,
        name: str,
        /,
        *,
        parent_id: undefined.UndefinedOr[snowflakes.Snowflake] = undefined.UNDEFINED,
        bitrate: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        video_quality_mode: undefined.UndefinedOr[typing.Union[channels.VideoQualityMode, int]] = undefined.UNDEFINED,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Collection[channels.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        region: undefined.UndefinedNoneOr[typing.Union[voices.VoiceRegion, str]],
        user_limit: undefined.UndefinedOr[int] = undefined.UNDEFINED,
    ) -> snowflakes.Snowflake:
        """Create a voice channel.

        Parameters
        ----------
        name : str
            The channels name. Must be between 2 and 1000 characters.

        Other Parameters
        ----------------
        position : hikari.undefined.UndefinedOr[int]
            If provided, the position of the channel (relative to the
            category, if any).
        user_limit : hikari.undefined.UndefinedOr[int]
            If provided, the maximum users in the channel at once.
            Must be between 0 and 99 with 0 meaning no limit.
        bitrate : hikari.undefined.UndefinedOr[int]
            If provided, the bitrate for the channel. Must be
            between 8000 and 96000 or 8000 and 128000 for VIP
            servers.
        video_quality_mode : hikari.undefined.UndefinedOr[typing.Union[hikari.channels.VideoQualityMode, int]]
            If provided, the new video quality mode for the channel.
        permission_overwrites : hikari.undefined.UndefinedOr[typing.Sequence[hikari.channels.PermissionOverwrite]]
            If provided, the permission overwrites for the channel.
        region : hikari.undefined.UndefinedOr[typing.Union[hikari.voices.VoiceRegion, str]]
             If provided, the voice region to for this channel. Passing
             `None` here will set it to "auto" mode where the used
             region will be decided based on the first person who connects to it
             when it's empty.
        parent_id : hikari.undefined.UndefinedOr[hikari.snowflakes.Snowflake]
            The ID of the category to create the channel under.

        Returns
        -------
        hikari.snowflakes.Snowflake
            The dummy ID for this channel that can be used temporarily to refer
            to this object while designing the guild layout.

            When the guild is created, this will be replaced with a different
            ID.
        """

    @abc.abstractmethod
    def add_stage_channel(
        self,
        name: str,
        /,
        *,
        parent_id: undefined.UndefinedOr[snowflakes.Snowflake] = undefined.UNDEFINED,
        bitrate: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Collection[channels.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        region: undefined.UndefinedNoneOr[typing.Union[voices.VoiceRegion, str]],
        user_limit: undefined.UndefinedOr[int] = undefined.UNDEFINED,
    ) -> snowflakes.Snowflake:
        """Create a stage channel.

        Parameters
        ----------
        name : str
            The channels name. Must be between 2 and 1000 characters.

        Other Parameters
        ----------------
        position : hikari.undefined.UndefinedOr[int]
            If provided, the position of the channel (relative to the
            category, if any).
        user_limit : hikari.undefined.UndefinedOr[int]
            If provided, the maximum users in the channel at once.
            Must be between 0 and 99 with 0 meaning no limit.
        bitrate : hikari.undefined.UndefinedOr[int]
            If provided, the bitrate for the channel. Must be
            between 8000 and 96000 or 8000 and 128000 for VIP
            servers.
        permission_overwrites : hikari.undefined.UndefinedOr[typing.Sequence[hikari.channels.PermissionOverwrite]]
            If provided, the permission overwrites for the channel.
        region : hikari.undefined.UndefinedOr[typing.Union[hikari.voices.VoiceRegion, str]]
             If provided, the voice region to for this channel. Passing
             `None` here will set it to "auto" mode where the used
             region will be decided based on the first person who connects to it
             when it's empty.
        parent_id : hikari.undefined.UndefinedOr[hikari.snowflakes.Snowflake]
            The ID of the category to create the channel under.

        Returns
        -------
        hikari.snowflakes.Snowflake
            The dummy ID for this channel that can be used temporarily to refer
            to this object while designing the guild layout.

            When the guild is created, this will be replaced with a different
            ID.
        """


class InteractionResponseBuilder(abc.ABC):
    """Base class for all interaction response builders used in the interaction server."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def type(self) -> typing.Union[int, base_interactions.ResponseType]:
        """Type of this response."""

    @abc.abstractmethod
    def build(
        self, entity_factory: entity_factory_.EntityFactory, /
    ) -> typing.Tuple[typing.MutableMapping[str, typing.Any], typing.Sequence[files.Resource[files.AsyncReader]]]:
        """Build a JSON object from this builder.

        Parameters
        ----------
        entity_factory : hikari.api.entity_factory.EntityFactory
            The entity factory to use to serialize entities within this builder.

        Returns
        -------
        typing.Tuple[typing.MutableMapping[str, typing.Any], typing.Sequence[files.Resource[Files.AsyncReader]]
            A tuple of the built json object representation of this builder and
            a sequence of up to 10 files to send with the response.
        """


class InteractionDeferredBuilder(InteractionResponseBuilder, abc.ABC):
    """Interface of a deferred message interaction response builder."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def type(self) -> base_interactions.DeferredResponseTypesT:
        """Type of this response."""

    @property
    @abc.abstractmethod
    def flags(self) -> typing.Union[undefined.UndefinedType, int, messages.MessageFlag]:
        """Message flags this response should have.

        .. note::
            As of writing the only message flag which can be set here is
            `hikari.messages.MessageFlag.EPHEMERAL`.
        """

    @abc.abstractmethod
    def set_flags(self, flags: typing.Union[undefined.UndefinedType, int, messages.MessageFlag], /) -> Self:
        """Set message flags for this response.

        .. note::
            As of writing, the only message flag which can be set is `hikari.messages.MessageFlag.EPHEMERAL`.

        Parameters
        ----------
        flags : typing.Union[hikari.undefined.UndefinedType, int, hikari.messages.MessageFlag]
            The message flags to set for this response.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder.
        """


class InteractionAutocompleteBuilder(InteractionResponseBuilder, abc.ABC):
    """Interface of an autocomplete interaction response builder."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def choices(self) -> typing.Sequence[commands.CommandChoice]:
        """Autocomplete choices."""

    @abc.abstractmethod
    def set_choices(self, choices: typing.Sequence[commands.CommandChoice], /) -> Self:
        """Set autocomplete choices.

        Returns
        -------
        InteractionAutocompleteBuilder
            Object of this builder.
        """


class InteractionMessageBuilder(InteractionResponseBuilder, abc.ABC):
    """Interface of an interaction message response builder used within REST servers.

    This can be returned by the listener registered to
    `hikari.api.interaction_server.InteractionServer` as a response to the interaction
    create.
    """

    __slots__: typing.Sequence[str] = ()

    # Required fields

    @property
    @abc.abstractmethod
    def type(self) -> base_interactions.MessageResponseTypesT:
        """Type of this response."""

    # Extendable fields

    @property
    @abc.abstractmethod
    def attachments(self) -> undefined.UndefinedNoneOr[typing.Sequence[files.Resourceish]]:
        """Sequence of up to 10 attachments to send with the message."""

    @property
    @abc.abstractmethod
    def components(self) -> undefined.UndefinedOr[typing.Sequence[ComponentBuilder]]:
        """Sequence of up to 5 component builders to send in this response."""

    @property
    @abc.abstractmethod
    def embeds(self) -> undefined.UndefinedOr[typing.Sequence[embeds_.Embed]]:
        """Sequence of up to 10 of the embeds included in this response."""

    # Settable fields

    @property
    @abc.abstractmethod
    def content(self) -> undefined.UndefinedOr[str]:
        """Response's message content."""

    @property
    @abc.abstractmethod
    def flags(self) -> typing.Union[undefined.UndefinedType, int, messages.MessageFlag]:
        """Message flags this response should have.

        .. note::
            As of writing the only message flag which can be set here is
            `hikari.messages.MessageFlag.EPHEMERAL`.
        """

    @property
    @abc.abstractmethod
    def is_tts(self) -> undefined.UndefinedOr[bool]:
        """Whether this response's content should be treated as text-to-speech."""

    @property
    @abc.abstractmethod
    def mentions_everyone(self) -> undefined.UndefinedOr[bool]:
        """Whether @everyone and @here mentions should be enabled for this response."""

    @property
    @abc.abstractmethod
    def role_mentions(
        self,
    ) -> undefined.UndefinedOr[typing.Union[snowflakes.SnowflakeishSequence[guilds.PartialRole], bool]]:
        """Whether and what role mentions should be enabled for this response.

        Either a sequence of object/IDs of the roles mentions should be enabled
        for, `False` or `hikari.undefined.UNDEFINED` to disallow any
        role mentions or `True` to allow all role mentions.
        """

    @property
    @abc.abstractmethod
    def user_mentions(
        self,
    ) -> undefined.UndefinedOr[typing.Union[snowflakes.SnowflakeishSequence[users.PartialUser], bool]]:
        """Whether and what user mentions should be enabled for this response.

        Either a sequence of object/IDs of the users mentions should be enabled
        for, `False` or `hikari.undefined.UNDEFINED` to disallow any
        user mentions or `True` to allow all user mentions.
        """

    @abc.abstractmethod
    def clear_attachments(self, /) -> Self:
        """Clear attachments for this response.

        This is only useful for message update responses, where you might want to
        remove all existing attachments.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder.
        """

    @abc.abstractmethod
    def add_attachment(self, attachment: files.Resourceish, /) -> Self:
        """Add an attachment to this response.

        Parameters
        ----------
        attachment : hikari.files.Resourceish
            The attachment to add.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder.
        """

    @abc.abstractmethod
    def add_component(self, component: ComponentBuilder, /) -> Self:
        """Add a component to this response.

        Parameters
        ----------
        component : ComponentBuilder
            The component builder to add to this response.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder.
        """

    @abc.abstractmethod
    def add_embed(self, embed: embeds_.Embed, /) -> Self:
        """Add an embed to this response.

        Parameters
        ----------
        embed : hikari.embeds.Embed
            Object of the embed to add to this response.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder to allow for chained calls.
        """

    @abc.abstractmethod
    def set_content(self, content: undefined.UndefinedOr[str], /) -> Self:
        """Set the response's message content.

        Parameters
        ----------
        content : hikari.undefined.UndefinedOr[str]
            The message content to set for this response.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder to allow for chained calls.
        """

    @abc.abstractmethod
    def set_flags(self, flags: typing.Union[undefined.UndefinedType, int, messages.MessageFlag], /) -> Self:
        """Set message flags for this response.

        .. note::
            As of writing, the only message flag which can be set is
            `hikari.messages.MessageFlag.EPHEMERAL`..

        Parameters
        ----------
        flags : typing.Union[hikari.undefined.UndefinedType, int, hikari.messages.MessageFlag]
            The message flags to set for this response.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder to allow for chained calls.
        """

    @abc.abstractmethod
    def set_tts(self, tts: undefined.UndefinedOr[bool], /) -> Self:
        """Set whether this response should trigger text-to-speech processing.

        Parameters
        ----------
        tts : bool
            Whether this response should trigger text-to-speech processing.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder to allow for chained calls.
        """

    @abc.abstractmethod
    def set_mentions_everyone(self, mentions: undefined.UndefinedOr[bool] = undefined.UNDEFINED, /) -> Self:
        """Set whether this response should be able to mention @everyone/@here.

        Parameters
        ----------
        mentions : hikari.undefined.UndefinedOr[bool]
            Whether this response should be able to mention @everyone/@here.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder to allow for chained calls.
        """

    @abc.abstractmethod
    def set_role_mentions(
        self,
        mentions: undefined.UndefinedOr[
            typing.Union[snowflakes.SnowflakeishSequence[guilds.PartialRole], bool]
        ] = undefined.UNDEFINED,
        /,
    ) -> Self:
        """Set whether and what role mentions should be possible for this response.

        Parameters
        ----------
        mentions : hikari.undefined.UndefinedOr[typing.Union[hikari.snowflakes.SnowflakeishSequence[hikari.users.PartialUser], bool]]
            Either a sequence of object/IDs of the roles mentions should be enabled for,
            `False` or `hikari.undefined.UNDEFINED` to disallow any role
            mentions or `True` to allow all role mentions.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder to allow for chained calls.
        """  # noqa: E501 - Line too long

    @abc.abstractmethod
    def set_user_mentions(
        self,
        mentions: undefined.UndefinedOr[
            typing.Union[snowflakes.SnowflakeishSequence[users.PartialUser], bool]
        ] = undefined.UNDEFINED,
        /,
    ) -> Self:
        """Set whether and what user mentions should be possible for this response.

        Parameters
        ----------
        mentions : hikari.undefined.UndefinedOr[typing.Union[hikari.snowflakes.SnowflakeishSequence[hikari.users.PartialUser], bool]]
            Either a sequence of object/IDs of the users mentions should be enabled for,
            `False` or `hikari.undefined.UNDEFINED` to disallow any user
            mentions or `True` to allow all user mentions.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder to allow for chained calls.
        """  # noqa: E501 - Line too long


class InteractionModalBuilder(InteractionResponseBuilder, abc.ABC):
    """Interface of an interaction modal response builder used within REST servers.

    This can be returned by the listener registered to
    `hikari.api.interaction_server.InteractionServer` as a response to the interaction
    create.
    """

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def type(self) -> typing.Literal[base_interactions.ResponseType.MODAL]:
        """Type of this response."""

    @property
    @abc.abstractmethod
    def title(self) -> str:
        """Title that will show up in the modal."""

    @property
    @abc.abstractmethod
    def custom_id(self) -> str:
        """Developer set custom ID used for identifying interactions with this modal."""

    @property
    @abc.abstractmethod
    def components(self) -> undefined.UndefinedOr[typing.Sequence[ComponentBuilder]]:
        """Sequence of component builders to send in this modal."""

    @abc.abstractmethod
    def set_title(self, title: str, /) -> Self:
        """Set the title that will show up in the modal.

        Parameters
        ----------
        title : str
            The title that will show up in the modal.
        """

    @abc.abstractmethod
    def set_custom_id(self, custom_id: str, /) -> Self:
        """Set the developer set custom ID used for identifying interactions with this modal.

        Parameters
        ----------
        custom_id : str
            The developer set custom ID used for identifying interactions with this modal.
        """

    @abc.abstractmethod
    def add_component(self, component: ComponentBuilder, /) -> Self:
        """Add a component to this modal.

        Parameters
        ----------
        component : ComponentBuilder
            The component builder to add to this modal.
        """


class CommandBuilder(abc.ABC):
    """Interface of a command builder used when bulk creating commands over REST."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def name(self) -> str:
        r"""Name to set for this command.

        .. warning::
            This should match the regex `^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$` in Unicode mode
            and must be lowercase.
        """

    @property
    @abc.abstractmethod
    def type(self) -> commands.CommandType:
        """Type of this command."""

    @property
    @abc.abstractmethod
    def id(self) -> undefined.UndefinedOr[snowflakes.Snowflake]:
        """ID of this command."""

    @property
    @abc.abstractmethod
    def default_member_permissions(self) -> typing.Union[undefined.UndefinedType, permissions_.Permissions, int]:
        """Member permissions necessary to utilize this command by default.

        If `0`, then it will be available for all members. Note that this doesn't affect
        administrators of the guild and overwrites.
        """

    @property
    @abc.abstractmethod
    def is_dm_enabled(self) -> undefined.UndefinedOr[bool]:
        """Whether this command is enabled in DMs with the bot.

        Only applicable to globally-scoped commands.
        """

    @property
    @abc.abstractmethod
    def is_nsfw(self) -> undefined.UndefinedOr[bool]:
        """Whether this command age-restricted."""

    @property
    @abc.abstractmethod
    def name_localizations(self) -> typing.Mapping[typing.Union[locales.Locale, str], str]:
        """Name localizations set for this command."""

    @abc.abstractmethod
    def set_id(self, id_: undefined.UndefinedOr[snowflakes.Snowflakeish], /) -> Self:
        """Set the ID of this command.

        Parameters
        ----------
        id_ : hikari.undefined.UndefinedOr[hikari.snowflakes.Snowflake]
            The ID to set for this command.

        Returns
        -------
        CommandBuilder
            Object of this command builder to allow for chained calls.
        """

    @abc.abstractmethod
    def set_default_member_permissions(
        self, default_member_permissions: typing.Union[undefined.UndefinedType, int, permissions_.Permissions], /
    ) -> Self:
        """Set the member permissions necessary to utilize this command by default.

        Parameters
        ----------
        default_member_permissions : hikari.undefined.UndefinedOr[bool]
            The default member permissions to utilize this command by default.

            If `0`, then it will be available for all members. Note that this doesn't affect
            administrators of the guild and overwrites.

        Returns
        -------
        CommandBuilder
            Object of this command builder.
        """

    @abc.abstractmethod
    def set_is_dm_enabled(self, state: undefined.UndefinedOr[bool], /) -> Self:
        """Set whether this command will be enabled in DMs with the bot.

        Parameters
        ----------
        state : hikari.undefined.UndefinedOr[bool]
            Whether this command is enabled in DMs with the bot.

        Returns
        -------
        CommandBuilder
            Object of this command builder to allow for chained calls.
        """

    @abc.abstractmethod
    def set_is_nsfw(self, state: undefined.UndefinedOr[bool], /) -> Self:
        """Set whether this command will be age-restricted.

        Parameters
        ----------
        state : hikari.undefined.UndefinedOr[bool]
            Whether this command is age-restricted.

        Returns
        -------
        CommandBuilder
            Object of this command builder for chained calls.
        """

    @abc.abstractmethod
    def set_name_localizations(
        self, name_localizations: typing.Mapping[typing.Union[locales.Locale, str], str], /
    ) -> Self:
        """Set the name localizations for this command.

        Parameters
        ----------
        name_localizations : typing.Mapping[typing.Union[hikari.locales.Locale, str], str]
            The name localizations to set for this command.

        Returns
        -------
        CommandBuilder
            Object of this command builder.
        """

    @abc.abstractmethod
    def build(self, entity_factory: entity_factory_.EntityFactory, /) -> typing.MutableMapping[str, typing.Any]:
        """Build a JSON object from this builder.

        Parameters
        ----------
        entity_factory : hikari.api.entity_factory.EntityFactory
            The entity factory to use to serialize entities within this builder.

        Returns
        -------
        typing.MutableMapping[str, typing.Any]
            The built json object representation of this builder.
        """

    @abc.abstractmethod
    async def create(
        self,
        rest: rest_api.RESTClient,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        /,
        *,
        guild: undefined.UndefinedOr[snowflakes.SnowflakeishOr[guilds.PartialGuild]] = undefined.UNDEFINED,
    ) -> commands.PartialCommand:
        """Create this command through a REST call.

        Parameters
        ----------
        rest : hikari.api.rest.RESTClient
            The REST client to use to make this request.
        application : hikari.snowflakes.SnowflakeishOr[hikari.guilds.PartialApplication]
            The application to create this command for.

        Other Parameters
        ----------------
        guild : hikari.undefined.UndefinedOr[hikari.snowflakes.SnowflakeishOr[hikari.guilds.PartialGuild]]
            The guild to create this command for.

            If left undefined then this command will be declared globally.

        Returns
        -------
        hikari.commands.PartialCommand
            The created command.
        """


class SlashCommandBuilder(CommandBuilder):
    """SlashCommandBuilder."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Command's description.

        .. warning::
            This should be inclusively between 1-100 characters in length.
        """

    @property
    @abc.abstractmethod
    def description_localizations(
        self,
    ) -> typing.Mapping[typing.Union[locales.Locale, str], str]:
        """Command's localised descriptions."""

    @abc.abstractmethod
    def set_description_localizations(
        self,
        description_localizations: typing.Mapping[typing.Union[locales.Locale, str], str],
        /,
    ) -> Self:
        """Set the localised descriptions for this command.

        Parameters
        ----------
        description_localizations : typing.Mapping[typing.Union[hikari.locales.Locale, str], str]
            The description localizations to set for this command.

        Returns
        -------
        CommandBuilder
            Object of this command builder.
        """

    @property
    @abc.abstractmethod
    def options(self) -> typing.Sequence[commands.CommandOption]:
        """Sequence of up to 25 of the options set for this command."""

    @abc.abstractmethod
    def add_option(self, option: commands.CommandOption) -> Self:
        """Add an option to this command.

        .. note::
            A command can have up to 25 options.

        Parameters
        ----------
        option : hikari.commands.CommandOption
            The option to add to this command.

        Returns
        -------
        CommandBuilder
            Object of this command builder to allow for chained calls.
        """

    @abc.abstractmethod
    async def create(
        self,
        rest: rest_api.RESTClient,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        /,
        *,
        guild: undefined.UndefinedOr[snowflakes.SnowflakeishOr[guilds.PartialGuild]] = undefined.UNDEFINED,
    ) -> commands.SlashCommand:
        """Create this command through a REST call.

        This is a shorthand for calling `hikari.api.rest.RESTClient.create_slash_command`
        with the builder's information.

        Parameters
        ----------
        rest : hikari.api.rest.RESTClient
            The REST client to use to make this request.
        application : hikari.snowflakes.SnowflakeishOr[hikari.guilds.PartialApplication]
            The application to create this command for.

        Other Parameters
        ----------------
        guild : hikari.undefined.UndefinedOr[hikari.snowflakes.SnowflakeishOr[hikari.guilds.PartialGuild]]
            The guild to create this command for.

            If left undefined then this command will be declared globally.

        Returns
        -------
        hikari.commands.SlashCommand
            The created command.
        """


class ContextMenuCommandBuilder(CommandBuilder):
    """ContextMenuCommandBuilder."""

    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    async def create(
        self,
        rest: rest_api.RESTClient,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        /,
        *,
        guild: undefined.UndefinedOr[snowflakes.SnowflakeishOr[guilds.PartialGuild]] = undefined.UNDEFINED,
    ) -> commands.ContextMenuCommand:
        """Create this command through a REST call.

        This is a shorthand for calling
        `hikari.api.rest.RESTClient.create_context_menu_command`
        with the builder's information.

        Parameters
        ----------
        rest : hikari.api.rest.RESTClient
            The REST client to use to make this request.
        application : hikari.snowflakes.SnowflakeishOr[hikari.guilds.PartialApplication]
            The application to create this command for.

        Other Parameters
        ----------------
        guild : hikari.undefined.UndefinedOr[hikari.snowflakes.SnowflakeishOr[hikari.guilds.PartialGuild]]
            The guild to create this command for.

            If left undefined then this command will be declared globally.

        Returns
        -------
        hikari.commands.ContextMenuCommand
            The created command.
        """


class ComponentBuilder(abc.ABC):
    """Base class for all component builder classes."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def type(self) -> typing.Union[int, components_.ComponentType]:
        """Type of component this builder represents."""

    @abc.abstractmethod
    def build(self) -> typing.MutableMapping[str, typing.Any]:
        """Build a JSON object from this builder.

        Returns
        -------
        typing.MutableMapping[str, typing.Any]
            The built json object representation of this builder.
        """


class ButtonBuilder(ComponentBuilder, abc.ABC, typing.Generic[_ContainerT]):
    """Builder class for a message button component."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def type(self) -> typing.Literal[components_.ComponentType.BUTTON]:
        """Type of component this builder represents."""

    @property
    @abc.abstractmethod
    def style(self) -> typing.Union[components_.ButtonStyle, int]:
        """Button's style."""

    @property
    @abc.abstractmethod
    def emoji(self) -> typing.Union[snowflakes.Snowflakeish, emojis.Emoji, str, undefined.UndefinedType]:
        """Emoji which should appear on this button."""

    @property
    @abc.abstractmethod
    def label(self) -> undefined.UndefinedOr[str]:
        """Text label which should appear on this button.

        .. note::
            The text label to that should appear on this button. This may be
            up to 80 characters long.
        """

    @property
    @abc.abstractmethod
    def is_disabled(self) -> bool:
        """Whether the button should be marked as disabled."""

    @abc.abstractmethod
    def set_emoji(
        self, emoji: typing.Union[snowflakes.Snowflakeish, emojis.Emoji, str, undefined.UndefinedType], /
    ) -> Self:
        """Set the emoji to display on this button.

        Parameters
        ----------
        emoji : typing.Union[hikari.snowflakes.Snowflakeish, hikari.emojis.Emoji, str, hikari.undefined.UndefinedType]
            Object, ID or raw string of the emoji which should be displayed on
            this button.

        Returns
        -------
        ButtonBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_label(self, label: undefined.UndefinedOr[str], /) -> Self:
        """Set the text label which should be displayed on this button.

        Parameters
        ----------
        label : hikari.undefined.UndefinedOr[str]
            The text label to show on this button.

            This may be up to 80 characters long.

        Returns
        -------
        ButtonBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_is_disabled(self, state: bool, /) -> Self:
        """Set whether this button should be disabled.

        Parameters
        ----------
        state : bool
            Whether this button should be disabled.

        Returns
        -------
        ButtonBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def add_to_container(self) -> _ContainerT:
        """Add this button to the container component it belongs to.

        This is used as the finalising call during chained calls.

        Returns
        -------
        _ContainerT
            The container component that owns this button.
        """


class LinkButtonBuilder(ButtonBuilder[_ContainerT], abc.ABC):
    """Builder interface for link buttons."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def url(self) -> str:
        """URL this button should link to when pressed."""


class InteractiveButtonBuilder(ButtonBuilder[_ContainerT], abc.ABC):
    """Builder interface for interactive buttons."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def custom_id(self) -> str:
        """Developer set custom ID used for identifying interactions with this button."""


class SelectOptionBuilder(abc.ABC, typing.Generic[_SelectMenuBuilderT]):
    """Builder class for select menu options."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def label(self) -> str:
        """User-facing name of the option, max 100 characters."""

    @property
    @abc.abstractmethod
    def value(self) -> str:
        """Developer-defined value of the option, max 100 characters."""

    @property
    @abc.abstractmethod
    def description(self) -> undefined.UndefinedOr[str]:
        """Description of the option, max 100 characters."""

    @property
    @abc.abstractmethod
    def emoji(self) -> typing.Union[snowflakes.Snowflakeish, emojis.Emoji, str, undefined.UndefinedType]:
        """Emoji which should appear on this option."""

    @property
    @abc.abstractmethod
    def is_default(self) -> bool:
        """Whether this option should be marked as selected by default."""

    @abc.abstractmethod
    def set_description(self, value: undefined.UndefinedOr[str], /) -> Self:
        """Set the option's description.

        Parameters
        ----------
        value : hikari.undefined.UndefinedOr[str]
            Description to set for this option. This can be up to 100 characters
            long.

        Returns
        -------
        SelectOptionBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_emoji(
        self, emoji: typing.Union[snowflakes.Snowflakeish, emojis.Emoji, str, undefined.UndefinedType], /
    ) -> Self:
        """Set the emoji to display on this option.

        Parameters
        ----------
        emoji : typing.Union[hikari.snowflakes.Snowflakeish, hikari.emojis.Emoji, str, hikari.undefined.UndefinedType]
            Object, ID or raw string of the emoji which should be displayed on
            this option.

        Returns
        -------
        SelectOptionBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_is_default(self, state: bool, /) -> Self:
        """Set whether this option should be selected by default.

        Parameters
        ----------
        state : bool
            Whether this option should be selected by default.

        Returns
        -------
        SelectOptionBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def add_to_menu(self) -> _SelectMenuBuilderT:
        """Add this option to the menu component it belongs to.

        This is used as the finalising call during chained calls.

        Returns
        -------
        _SelectMenuBuilderT
            The menu component that owns this button.
        """

    @abc.abstractmethod
    def build(self) -> typing.MutableMapping[str, typing.Any]:
        """Build a JSON object from this builder.

        Returns
        -------
        typing.MutableMapping[str, typing.Any]
            The built json object representation of this builder.
        """


class SelectMenuBuilder(ComponentBuilder, abc.ABC, typing.Generic[_ContainerT]):
    """Builder class for a select menu."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def custom_id(self) -> str:
        """Developer set custom ID used for identifying interactions with this menu."""

    @property
    @abc.abstractmethod
    def is_disabled(self) -> bool:
        """Whether the select menu should be marked as disabled."""

    @property
    @abc.abstractmethod
    def placeholder(self) -> undefined.UndefinedOr[str]:
        """Placeholder text to display when no options are selected."""

    @property
    @abc.abstractmethod
    def min_values(self) -> int:
        """Minimum number of options which must be chosen.

        Defaults to 1.
        Must be less than or equal to `SelectMenuBuilder.max_values` and greater
        than or equal to 0.
        """

    @property
    @abc.abstractmethod
    def max_values(self) -> int:
        """Maximum number of options which can be chosen.

        Defaults to 1.
        Must be greater than or equal to `SelectMenuBuilder.min_values` and
        less than or equal to 25.
        """

    @abc.abstractmethod
    def set_is_disabled(self, state: bool, /) -> Self:
        """Set whether this option is disabled.

        Defaults to `False`.

        Parameters
        ----------
        state : bool
            Whether this option is disabled.

        Returns
        -------
        SelectMenuBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_placeholder(self, value: undefined.UndefinedOr[str], /) -> Self:
        """Set place-holder text to be shown when no option is selected.

        Parameters
        ----------
        value : hikari.undefined.UndefinedOr[str]
            Place-holder text to be displayed when no option is selected.
            Max 100 characters.

        Returns
        -------
        SelectMenuBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_min_values(self, value: int, /) -> Self:
        """Set the minimum amount of options which need to be selected for this menu.

        .. note::
            This defaults to 1 if not set and must be greater than or equal to 0
            and less than or equal to `SelectMenuBuilder.max_values`.

        Parameters
        ----------
        value : int
            The minimum amount of options which need to be selected for this menu.

        Returns
        -------
        SelectMenuBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_max_values(self, value: int, /) -> Self:
        """Set the maximum amount of options which can be selected for this menu.

        .. note::
            This defaults to 1 if not set and must be less than or equal to 25
            and greater than or equal to `SelectMenuBuilder.min_values`.

        Parameters
        ----------
        value : int
            The maximum amount of options which can selected for this menu.

        Returns
        -------
        SelectMenuBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def add_to_container(self) -> _ContainerT:
        """Finalise this builder by adding it to its parent container component.

        Returns
        -------
        _ContainerT
            The parent container component builder.
        """


class TextSelectMenuBuilder(SelectMenuBuilder[_ContainerT], abc.ABC, typing.Generic[_ContainerT]):
    """Builder class for a text select menu."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def options(self) -> typing.Sequence[SelectOptionBuilder[Self]]:
        """Sequence of the options set for this select menu."""

    @abc.abstractmethod
    def add_option(self, label: str, value: str, /) -> SelectOptionBuilder[Self]:
        """Add an option to this menu.

        .. note::
            Setup should be finalised by calling `add_to_menu` in the builder
            returned.

        Parameters
        ----------
        label : str
            The user-facing name of this option, max 100 characters.
        value : str
            The developer defined value of this option, max 100 characters.

        Returns
        -------
        SelectOptionBuilder[SelectMenuBuilder]
            Option builder object.
        """


class ChannelSelectMenuBuilder(SelectMenuBuilder[_ContainerT], abc.ABC, typing.Generic[_ContainerT]):
    """Builder class for a channel select menu."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def channel_types(self) -> typing.Sequence[channels.ChannelType]:
        """The channel types that can be selected in this menu."""

    @abc.abstractmethod
    def set_channel_types(self, value: typing.Sequence[channels.ChannelType], /) -> Self:
        """Set the valid channel types for this menu.

        Parameters
        ----------
        value : typing.Sequence[hikari.channels.ChannelType]
            The valid channel types for this menu.

        Returns
        -------
        SelectMenuBuilder
            The builder object to enable chained calls.
        """


class TextInputBuilder(ComponentBuilder, abc.ABC, typing.Generic[_ContainerT]):
    """Builder class for text inputs components."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def type(self) -> typing.Literal[components_.ComponentType.TEXT_INPUT]:
        """Type of component this builder represents."""

    @property
    @abc.abstractmethod
    def custom_id(self) -> str:
        """Developer set custom ID used for identifying this text input.

        .. note::
            This custom_id is never used in component interaction events.
            It is meant to be used purely for resolving components modal interactions.
        """

    @property
    @abc.abstractmethod
    def label(self) -> str:
        """Label above this text input."""

    @property
    @abc.abstractmethod
    def style(self) -> components_.TextInputStyle:
        """Style to use for the text input."""

    @property
    @abc.abstractmethod
    def placeholder(self) -> undefined.UndefinedOr[str]:
        """Placeholder text for when the text input is empty."""

    @property
    @abc.abstractmethod
    def value(self) -> undefined.UndefinedOr[str]:
        """Pre-filled text that will be sent if the user does not write anything."""

    @property
    @abc.abstractmethod
    def required(self) -> undefined.UndefinedOr[bool]:
        """Whether this text input is required to be filled-in."""

    @property
    @abc.abstractmethod
    def min_length(self) -> undefined.UndefinedOr[int]:
        """Minimum length the text should have."""

    @property
    @abc.abstractmethod
    def max_length(self) -> undefined.UndefinedOr[int]:
        """Maximum length the text should have."""

    @abc.abstractmethod
    def set_style(self, style: typing.Union[components_.TextInputStyle, int], /) -> Self:
        """Set the style to use for the text input.

        Parameters
        ----------
        style : typing.Union[hikari.modal_interactions.TextInputStyle, int]
            Style to use for the text input.

        Returns
        -------
        TextInputBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_custom_id(self, custom_id: str, /) -> Self:
        """Set the developer set custom ID used for identifying this text input.

        Parameters
        ----------
        custom_id : str
            Developer set custom ID used for identifying this text input.

        Returns
        -------
        TextInputBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_label(self, label: str, /) -> Self:
        """Set the label above this text input.

        Parameters
        ----------
        label : str
            Label above this text input.

        Returns
        -------
        TextInputBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_placeholder(self, placeholder: str, /) -> Self:
        """Set the placeholder text for when the text input is empty.

        Parameters
        ----------
        placeholder : str:
            Placeholder text that will disappear when the user types anything.

        Returns
        -------
        TextInputBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_value(self, value: str, /) -> Self:
        """Pre-filled text that will be sent if the user does not write anything.

        Parameters
        ----------
        value : str
            Pre-filled text that will be sent if the user does not write anything.

        Returns
        -------
        TextInputBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_required(self, required: bool, /) -> Self:
        """Set whether this text input is required to be filled-in.

        Parameters
        ----------
        required : bool
            Whether this text input is required to be filled-in.

        Returns
        -------
        TextInputBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_min_length(self, min_length: int, /) -> Self:
        """Set the minimum length the text should have.

        Parameters
        ----------
        min_length : int
            The minimum length the text should have.

        Returns
        -------
        TextInputBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def set_max_length(self, max_length: int, /) -> Self:
        """Set the maximum length the text should have.

        Parameters
        ----------
        max_length : int
            The maximum length the text should have.

        Returns
        -------
        TextInputBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def add_to_container(self) -> _ContainerT:
        """Finalise this builder by adding it to its parent container component.

        Returns
        -------
        _ContainerT
            The parent container component builder.
        """


class MessageActionRowBuilder(ComponentBuilder, abc.ABC):
    """Builder class for action row components."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def type(self) -> typing.Literal[components_.ComponentType.ACTION_ROW]:
        """Type of component this builder represents."""

    @property
    @abc.abstractmethod
    def components(self) -> typing.Sequence[ComponentBuilder]:
        """Sequence of the component builders registered within this action row."""

    @abc.abstractmethod
    def add_component(self, component: ComponentBuilder, /) -> Self:
        """Add a component to this action row builder.

        .. warning::
            It is generally better to use `ActionRowBuilder.add_button`
            and `ActionRowBuilder.add_select_menu` to add your
            component to the builder. Those methods utilize this one.

        Parameters
        ----------
        component : ComponentBuilder
            The component builder to add to the action row.

        Returns
        -------
        ActionRowBuilder
            The builder object to enable chained calls.
        """

    @typing.overload
    @abc.abstractmethod
    def add_button(
        self, style: components_.InteractiveButtonTypesT, custom_id: str, /
    ) -> InteractiveButtonBuilder[Self]:
        ...

    @typing.overload
    @abc.abstractmethod
    def add_button(
        self, style: typing.Literal[components_.ButtonStyle.LINK, 5], url: str, /
    ) -> LinkButtonBuilder[Self]:
        ...

    @typing.overload
    @abc.abstractmethod
    def add_button(
        self, style: typing.Union[int, components_.ButtonStyle], url_or_custom_id: str, /
    ) -> typing.Union[LinkButtonBuilder[Self], InteractiveButtonBuilder[Self]]:
        ...

    @abc.abstractmethod
    def add_button(
        self, style: typing.Union[int, components_.ButtonStyle], url_or_custom_id: str, /
    ) -> typing.Union[LinkButtonBuilder[Self], InteractiveButtonBuilder[Self]]:
        """Add a button component to this action row builder.

        Parameters
        ----------
        style : typing.Union[int, hikari.messages.ButtonStyle]
            The button's style.
        url_or_custom_id : str
            For interactive button styles this is a developer-defined custom
            identifier used to identify which button triggered component interactions.

            For Link button styles this is the URL the link button should redirect
            to.

        Returns
        -------
        typing.Union[LinkButtonBuilder[Self], InteractiveButtonBuilder[Self]]
            Button builder object.
            `ButtonBuilder.add_to_container` should be called to finalise the
            component.
        """

    @typing.overload  # Deprecated overload
    @abc.abstractmethod
    def add_select_menu(
        self,
        custom_id: str,
        /,
    ) -> TextSelectMenuBuilder[Self]:
        ...

    @typing.overload
    @abc.abstractmethod
    def add_select_menu(
        self,
        type_: typing.Literal[components_.ComponentType.TEXT_SELECT_MENU, 3],
        custom_id: str,
        /,
    ) -> TextSelectMenuBuilder[Self]:
        ...

    @typing.overload
    @abc.abstractmethod
    def add_select_menu(
        self,
        type_: typing.Literal[components_.ComponentType.CHANNEL_SELECT_MENU, 8],
        custom_id: str,
        /,
    ) -> ChannelSelectMenuBuilder[Self]:
        ...

    @typing.overload
    @abc.abstractmethod
    def add_select_menu(
        self,
        type_: typing.Union[components_.ComponentType, int],
        custom_id: str,
        /,
    ) -> SelectMenuBuilder[Self]:
        ...

    @abc.abstractmethod
    def add_select_menu(
        self,
        type_: typing.Union[components_.ComponentType, int, str],
        # These have default during the deprecation period for backwards compatibility, as custom_id
        # used to come first
        custom_id: str = "",
        /,
    ) -> SelectMenuBuilder[Self]:
        """Add a select menu component to this action row builder.

        .. deprecated:: 2.0.0.dev116
            `type_` now comes as a positional-only argument before `custom_id`.

        Parameters
        ----------
        type_ : typing.Union[hikari.components.ComponentType, int]
            The type for the select menu.
        custom_id : str
            A developer-defined custom identifier used to identify which menu
            triggered component interactions.

        Returns
        -------
        SelectMenuBuilder[Self]
            Select menu builder object.
            `SelectMenuBuilder.add_to_container` should be called to finalise the
            component.

        Raises
        ------
        ValueError
            If an invalid select menu type is passed.
        """


class ModalActionRowBuilder(ComponentBuilder, abc.ABC):
    """Builder class for modal action row components."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def type(self) -> typing.Literal[components_.ComponentType.ACTION_ROW]:
        """Type of component this builder represents."""

    @property
    @abc.abstractmethod
    def components(self) -> typing.Sequence[ComponentBuilder]:
        """Sequence of the component builders registered within this action row."""

    @abc.abstractmethod
    def add_component(
        self,
        component: ComponentBuilder,
        /,
    ) -> Self:
        """Add a component to this action row builder.

        .. warning::
            It is generally better to use `ActionRowBuilder.add_button`
            and `ActionRowBuilder.add_select_menu` to add your
            component to the builder. Those methods utilize this one.

        Parameters
        ----------
        component : ComponentBuilder
            The component builder to add to the action row.

        Returns
        -------
        ActionRowBuilder
            The builder object to enable chained calls.
        """

    @abc.abstractmethod
    def add_text_input(
        self,
        custom_id: str,
        label: str,
    ) -> TextInputBuilder[Self]:
        """Add a text input component to this action row builder.

        Parameters
        ----------
        custom_id : str
            Developer set custom ID used for identifying this text input.
        label : str
            Label above this text input.

        Returns
        -------
        TextInputBuilder[Self]
            Text input builder object.
            `TextInputBuilder.add_to_container` should be called to finalise the
            component.
        """
