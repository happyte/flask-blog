from flask import url_for, request, current_app
from markupsafe import Markup

from . import get_renderer


class NavigationItem(object):
    """Base for all items in a Navigation.

    Every item inside a navigational view should derive from this class.
    """

    #: Indicates whether or not the item represents the currently active route
    active = False

    def render(self, renderer=None, **kwargs):
        """Render the navigational item using a renderer.

        :param renderer: An object implementing the :class:`~.Renderer`
                         interface.
        :return: A markupsafe string with the rendered result.
        """
        return Markup(get_renderer(current_app, renderer)(**kwargs).visit(
            self))


class Link(NavigationItem):
    """An item that contains a link to a destination and a title."""

    def __init__(self, text, dest):
        self.text = text
        self.dest = dest

    def get_url(self):
        return self.dest


class RawTag(NavigationItem):
    """An item usually expressed by a single HTML tag.

    :param title: The text inside the tag.
    :param attribs: Attributes on the item.
    """

    def __init__(self, content, **attribs):
        self.content = content
        self.attribs = attribs


class View(Link):
    """Application-internal link.

    The ``endpoint``, ``*args`` and ``**kwargs`` are passed on to
    :func:`~flask.url_for` to get the link.

    :param text: The text for the link.
    :param endpoint: The name of the view.
    :param kwargs: Extra keyword arguments for :func:`~flask.url_for`
    """

    #: Whether or not to consider query arguments (``?foo=bar&baz=1``) when
    #: determining whether or not a ``View`` is active.

    #: By default, query arguments are ignored."""
    ignore_query = True

    def __init__(self, text, endpoint, **kwargs):
        self.text = text
        self.endpoint = endpoint
        self.url_for_kwargs = kwargs

    def get_url(self):
        """Return url for this item.

        :return: A string with a link.
        """
        return url_for(self.endpoint, **self.url_for_kwargs)

    @property
    def active(self):
        if not request.endpoint == self.endpoint:
            return False

        # rebuild the url and compare results. we can't rely on using get_url()
        # because whether or not an external url is created depends on factors
        # outside our control

        _, url = request.url_rule.build(self.url_for_kwargs,
                                        append_unknown=not self.ignore_query)

        if self.ignore_query:
            return url == request.path

        # take query string into account.
        # FIXME: ensure that the order of query parameters is consistent
        return url == request.full_path


class Separator(NavigationItem):
    """Separator.

    A seperator inside the main navigational menu or a Subgroup. Not all
    renderers render these (or sometimes only inside Subgroups).
    """
    pass


class Subgroup(NavigationItem):
    """Nested substructure.

    Usually used to express a submenu.

    :param title: The title to display (i.e. when using dropdown-menus, this
                  text will be on the button).
    :param items: Any number of :class:`.NavigationItem` instances  that
                  make up the navigation element.
    """

    def __init__(self, title, *items):
        self.title = title
        self.items = list(items)

    @property
    def active(self):
        return any(item.active for item in self.items)


class Text(NavigationItem):
    """Label text.

    Not a ``<label>`` text, but a text label nonetheless. Precise
    representation is up to the renderer, but most likely something like
    ``<span>``, ``<div>`` or similar.
    """

    def __init__(self, text):
        self.text = text


class Navbar(Subgroup):
    """Top level navbar."""
    pass
