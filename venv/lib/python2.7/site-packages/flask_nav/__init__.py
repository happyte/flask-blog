import collections
from importlib import import_module
import re


def register_renderer(app, id, renderer, force=True):
    """Registers a renderer on the application.

    :param app: The :class:`~flask.Flask` application to register the renderer
                on
    :param id: Internal id-string for the renderer
    :param renderer: Renderer to register
    :param force: Whether or not to overwrite the renderer if a different one
                  is already registered for ``id``
    """
    renderers = app.extensions.setdefault('nav_renderers', {})

    if force:
        renderers[id] = renderer
    else:
        renderers.setdefault(id, renderer)


def get_renderer(app, id):
    """Retrieve a renderer.

    :param app: :class:`~flask.Flask` application to look ``id`` up on
    :param id: Internal renderer id-string to look up
    """
    renderer = app.extensions.get('nav_renderers', {})[id]

    if isinstance(renderer, tuple):
        mod_name, cls_name = renderer
        mod = import_module(mod_name)

        cls = mod
        for name in cls_name.split('.'):
            cls = getattr(cls, name)

        return cls

    return renderer


class NavbarRenderingError(Exception):
    pass


class ElementRegistry(collections.MutableMapping):
    def __init__(self):
        self._elems = {}

    def __getitem__(self, key):
        item = self._elems[key]

        if callable(item):
            try:
                return item()
            except Exception as e:
                # we wrap the exception, because otherwise things get
                # confusing if __getitem__ returns a KeyError

                # fixme: could use raise_from here on Py3
                raise NavbarRenderingError(
                    'Encountered {!r} while trying to render navbar'.format(e))

        return item

    def __setitem__(self, key, value):
        self._elems[key] = value

    def __delitem__(self, key):
        del self._elems[key]

    def __iter__(self):
        for key in self._elems.keys():
            return self[key]

    def __len__(self):
        return len(self._elems)


class Nav(object):
    """The Flask-Nav extension.

    :param app: An optional :class:`~flask.Flask` app to initialize.
    """

    def __init__(self, app=None):
        self.elems = ElementRegistry()

        # per default, register the simple renderer
        simple = __name__ + '.renderers', 'SimpleRenderer'
        self._renderers = [('simple', simple), (None, simple, False), ]

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize an application.

        :param app: A :class:`~flask.Flask` app.
        """
        if not hasattr(app, 'extensions'):
            app.extensions = {}

        app.extensions['nav'] = self
        app.add_template_global(self.elems, 'nav')

        # register some renderers
        for args in self._renderers:
            register_renderer(app, *args)

    def navigation(self, id=None):
        """Function decorator for navbar registration.

        Convenience function, calls :meth:`.register_element` with ``id`` and
        the decorated function as ``elem``.

        :param id: ID to pass on. If ``None``, uses the decorated functions
                   name.
        """

        def wrapper(f):
            self.register_element(id or f.__name__, f)
            return f

        return wrapper

    def register_element(self, id, elem):
        """Register navigational element.

        Registers the given navigational element, making it available using the
        id ``id``.

        This means that inside any template, the registered element will be
        available as ``nav.`` *id*.

        If ``elem`` is callable, any attempt to retrieve it inside the template
        will instead result in ``elem`` being called and the result being
        returned.

        :param id: Id to register element with
        :param elem: Element to register
        """
        self.elems[id] = elem

    def renderer(self, id=None, force=True):
        """Class decorator for Renderers.

        The decorated class will be added to the list of renderers kept by this
        instance that will be registered on the app upon app initialization.

        :param id: Id for the renderer, defaults to the class name in snake
                   case.
        :param force: Whether or not to overwrite existing renderers.
        """

        def _(cls):
            name = cls.__name__
            sn = name[0] + re.sub(r'([A-Z])', r'_\1', name[1:])

            self._renderers.append((id or sn.lower(), cls, force))
            return cls

        return _
