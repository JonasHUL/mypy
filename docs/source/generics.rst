Generics
========

This section explains how you can define your own generic classes that take
one or more type parameters, similar to built-in types such as ``list[X]``.
User-defined generics are a moderately advanced feature and you can get far
without ever using them -- feel free to skip this section and come back later.

.. _generic-classes:

Defining generic classes
************************

The built-in collection classes are generic classes. Generic types
have one or more type parameters, which can be arbitrary types. For
example, ``dict[int, str]`` has the type parameters ``int`` and
``str``, and ``list[int]`` has a type parameter ``int``.

Programs can also define new generic classes. Here is a very simple
generic class that represents a stack:

.. code-block:: python

   from typing import TypeVar, Generic

   T = TypeVar('T')

   class Stack(Generic[T]):
       def __init__(self) -> None:
           # Create an empty list with items of type T
           self.items: list[T] = []

       def push(self, item: T) -> None:
           self.items.append(item)

       def pop(self) -> T:
           return self.items.pop()

       def empty(self) -> bool:
           return not self.items

The ``Stack`` class can be used to represent a stack of any type:
``Stack[int]``, ``Stack[tuple[int, str]]``, etc.

Using ``Stack`` is similar to built-in container types:

.. code-block:: python

   # Construct an empty Stack[int] instance
   stack = Stack[int]()
   stack.push(2)
   stack.pop()
   stack.push('x')  # error: Argument 1 to "push" of "Stack" has incompatible type "str"; expected "int"

Construction of instances of generic types is type checked:

.. code-block:: python

   class Box(Generic[T]):
       def __init__(self, content: T) -> None:
           self.content = content

   Box(1)       # OK, inferred type is Box[int]
   Box[int](1)  # Also OK
   Box[int]('some string')  # error: Argument 1 to "Box" has incompatible type "str"; expected "int"

.. _generic-subclasses:

Defining subclasses of generic classes
**************************************

User-defined generic classes and generic classes defined in :py:mod:`typing`
can be used as a base class for another class (generic or non-generic). For example:

.. code-block:: python

   from typing import Generic, TypeVar, Mapping, Iterator

   KT = TypeVar('KT')
   VT = TypeVar('VT')

   # This is a generic subclass of Mapping
   class MyMap(Mapping[KT, VT]):
       def __getitem__(self, k: KT) -> VT: ...
       def __iter__(self) -> Iterator[KT]: ...
       def __len__(self) -> int: ...

   items: MyMap[str, int]  # OK

   # This is a non-generic subclass of dict
   class StrDict(dict[str, str]):
       def __str__(self) -> str:
           return f'StrDict({super().__str__()})'


   data: StrDict[int, int]  # Error! StrDict is not generic
   data2: StrDict  # OK

   # This is a user-defined generic class
   class Receiver(Generic[T]):
       def accept(self, value: T) -> None: ...

   # This is a generic subclass of Receiver
   class AdvancedReceiver(Receiver[T]): ...

.. note::

    You have to add an explicit :py:class:`~typing.Mapping` base class
    if you want mypy to consider a user-defined class as a mapping (and
    :py:class:`~typing.Sequence` for sequences, etc.). This is because mypy doesn't use
    *structural subtyping* for these ABCs, unlike simpler protocols
    like :py:class:`~typing.Iterable`, which use :ref:`structural subtyping <protocol-types>`.

:py:class:`Generic <typing.Generic>` can be omitted from bases if there are
other base classes that include type variables, such as ``Mapping[KT, VT]``
in the above example. If you include ``Generic[...]`` in bases, then
it should list all type variables present in other bases (or more,
if needed). The order of type variables is defined by the following
rules:

* If ``Generic[...]`` is present, then the order of variables is
  always determined by their order in ``Generic[...]``.
* If there are no ``Generic[...]`` in bases, then all type variables
  are collected in the lexicographic order (i.e. by first appearance).

For example:

.. code-block:: python

   from typing import Generic, TypeVar, Any

   T = TypeVar('T')
   S = TypeVar('S')
   U = TypeVar('U')

   class One(Generic[T]): ...
   class Another(Generic[T]): ...

   class First(One[T], Another[S]): ...
   class Second(One[T], Another[S], Generic[S, U, T]): ...

   x: First[int, str]        # Here T is bound to int, S is bound to str
   y: Second[int, str, Any]  # Here T is Any, S is int, and U is str

.. _generic-functions:

Generic functions
*****************

Type variables can be used to define generic functions:

.. code-block:: python

   from typing import TypeVar, Sequence

   T = TypeVar('T')

   # A generic function!
   def first(seq: Sequence[T]) -> T:
       return seq[0]

As with generic classes, the type variable can be replaced with any
type. That means ``first`` can be used with any sequence type, and the
return type is derived from the sequence item type. For example:

.. code-block:: python

   reveal_type(first([1, 2, 3]))   # Revealed type is "builtins.int"
   reveal_type(first(['a', 'b']))  # Revealed type is "builtins.str"

Note also that a single definition of a type variable (such as ``T``
above) can be used in multiple generic functions or classes. In this
example we use the same type variable in two generic functions:

.. code-block:: python

   from typing import TypeVar, Sequence

   T = TypeVar('T')      # Declare type variable

   def first(seq: Sequence[T]) -> T:
       return seq[0]

   def last(seq: Sequence[T]) -> T:
       return seq[-1]

A variable cannot have a type variable in its type unless the type
variable is bound in a containing generic class or function.

.. _generic-methods-and-generic-self:

Generic methods and generic self
********************************

You can also define generic methods — just use a type variable in the
method signature that is different from class type variables. In
particular, the ``self`` argument may also be generic, allowing a
method to return the most precise type known at the point of access.
In this way, for example, you can type check a chain of setter
methods:

.. code-block:: python

   from typing import TypeVar

   T = TypeVar('T', bound='Shape')

   class Shape:
       def set_scale(self: T, scale: float) -> T:
           self.scale = scale
           return self

   class Circle(Shape):
       def set_radius(self, r: float) -> 'Circle':
           self.radius = r
           return self

   class Square(Shape):
       def set_width(self, w: float) -> 'Square':
           self.width = w
           return self

   circle: Circle = Circle().set_scale(0.5).set_radius(2.7)
   square: Square = Square().set_scale(0.5).set_width(3.2)

Without using generic ``self``, the last two lines could not be type
checked properly, since the return type of ``set_scale`` would be
``Shape``, which doesn't define ``set_radius`` or ``set_width``.

Other uses are factory methods, such as copy and deserialization.
For class methods, you can also define generic ``cls``, using :py:class:`Type[T] <typing.Type>`:

.. code-block:: python

   from typing import TypeVar, Type

   T = TypeVar('T', bound='Friend')

   class Friend:
       other: "Friend" = None

       @classmethod
       def make_pair(cls: Type[T]) -> tuple[T, T]:
           a, b = cls(), cls()
           a.other = b
           b.other = a
           return a, b

   class SuperFriend(Friend):
       pass

   a, b = SuperFriend.make_pair()

Note that when overriding a method with generic ``self``, you must either
return a generic ``self`` too, or return an instance of the current class.
In the latter case, you must implement this method in all future subclasses.

Note also that mypy cannot always verify that the implementation of a copy
or a deserialization method returns the actual type of self. Therefore
you may need to silence mypy inside these methods (but not at the call site),
possibly by making use of the ``Any`` type or a ``# type: ignore`` comment.

Note that mypy lets you use generic self types in certain unsafe ways
in order to support common idioms. For example, using a generic
self type in an argument type is accepted even though it's unsafe:

.. code-block:: python

   from typing import TypeVar

   T = TypeVar("T")

   class Base:
       def compare(self: T, other: T) -> bool:
           return False

   class Sub(Base):
       def __init__(self, x: int) -> None:
           self.x = x

       # This is unsafe (see below) but allowed because it's
       # a common pattern and rarely causes issues in practice.
       def compare(self, other: Sub) -> bool:
           return self.x > other.x

   b: Base = Sub(42)
   b.compare(Base())  # Runtime error here: 'Base' object has no attribute 'x'

For some advanced uses of self types, see :ref:`additional examples <advanced_self>`.

Automatic self types using typing.Self
**************************************

Since the patterns described above are quite common, mypy supports a
simpler syntax, introduced in :pep:`673`, to make them easier to use.
Instead of defining a type variable and using an explicit annotation
for ``self``, you can import the special type ``typing.Self`` that is
automatically transformed into a type variable with the current class
as the upper bound, and you don't need an annotation for ``self`` (or
``cls`` in class methods). The example from the previous section can
be made simpler by using ``Self``:

.. code-block:: python

   from typing import Self

   class Friend:
       other: Self | None = None

       @classmethod
       def make_pair(cls) -> tuple[Self, Self]:
           a, b = cls(), cls()
           a.other = b
           b.other = a
           return a, b

   class SuperFriend(Friend):
       pass

   a, b = SuperFriend.make_pair()

This is more compact than using explicit type variables. Also, you can
use ``Self`` in attribute annotations in addition to methods.

.. note::

   To use this feature on Python versions earlier than 3.11, you will need to
   import ``Self`` from ``typing_extensions`` (version 4.0 or newer).

.. _variance-of-generics:

Variance of generic types
*************************

There are three main kinds of generic types with respect to subtype
relations between them: invariant, covariant, and contravariant.
Assuming that we have a pair of types ``A`` and ``B``, and ``B`` is
a subtype of ``A``, these are defined as follows:

* A generic class ``MyCovGen[T]`` is called covariant in type variable
  ``T`` if ``MyCovGen[B]`` is always a subtype of ``MyCovGen[A]``.
* A generic class ``MyContraGen[T]`` is called contravariant in type
  variable ``T`` if ``MyContraGen[A]`` is always a subtype of
  ``MyContraGen[B]``.
* A generic class ``MyInvGen[T]`` is called invariant in ``T`` if neither
  of the above is true.

Let us illustrate this by few simple examples:

.. code-block:: python

    # We'll use these classes in the examples below
    class Shape: ...
    class Triangle(Shape): ...
    class Square(Shape): ...

* Most immutable containers, such as :py:class:`~typing.Sequence` and
  :py:class:`~typing.FrozenSet` are covariant. :py:data:`~typing.Union` is
  also covariant in all variables: ``Union[Triangle, int]`` is
  a subtype of ``Union[Shape, int]``.

  .. code-block:: python

    def count_lines(shapes: Sequence[Shape]) -> int:
        return sum(shape.num_sides for shape in shapes)

    triangles: Sequence[Triangle]
    count_lines(triangles)  # OK

    def foo(triangle: Triangle, num: int):
        shape_or_number: Union[Shape, int]
        # a Triangle is a Shape, and a Shape is a valid Union[Shape, int]
        shape_or_number = triangle

  Covariance should feel relatively intuitive, but contravariance and invariance
  can be harder to reason about.

* :py:data:`~typing.Callable` is an example of type that behaves contravariant
  in types of arguments. That is, ``Callable[[Shape], int]`` is a subtype of
  ``Callable[[Triangle], int]``, despite ``Shape`` being a supertype of
  ``Triangle``. To understand this, consider:

  .. code-block:: python

    def cost_of_paint_required(
        triangle: Triangle,
        area_calculator: Callable[[Triangle], float]
    ) -> float:
        return area_calculator(triangle) * DOLLAR_PER_SQ_FT

    # This straightforwardly works
    def area_of_triangle(triangle: Triangle) -> float: ...
    cost_of_paint_required(triangle, area_of_triangle)  # OK

    # But this works as well!
    def area_of_any_shape(shape: Shape) -> float: ...
    cost_of_paint_required(triangle, area_of_any_shape)  # OK

  ``cost_of_paint_required`` needs a callable that can calculate the area of a
  triangle. If we give it a callable that can calculate the area of an
  arbitrary shape (not just triangles), everything still works.

* :py:class:`~typing.List` is an invariant generic type. Naively, one would think
  that it is covariant, like :py:class:`~typing.Sequence` above, but consider this code:

  .. code-block:: python

     class Circle(Shape):
         # The rotate method is only defined on Circle, not on Shape
         def rotate(self): ...

     def add_one(things: list[Shape]) -> None:
         things.append(Shape())

     my_circles: list[Circle] = []
     add_one(my_circles)     # This may appear safe, but...
     my_circles[-1].rotate()  # ...this will fail, since my_circles[0] is now a Shape, not a Circle

  Another example of invariant type is :py:class:`~typing.Dict`. Most mutable containers
  are invariant.

By default, mypy assumes that all user-defined generics are invariant.
To declare a given generic class as covariant or contravariant use
type variables defined with special keyword arguments ``covariant`` or
``contravariant``. For example:

.. code-block:: python

   from typing import Generic, TypeVar

   T_co = TypeVar('T_co', covariant=True)

   class Box(Generic[T_co]):  # this type is declared covariant
       def __init__(self, content: T_co) -> None:
           self._content = content

       def get_content(self) -> T_co:
           return self._content

   def look_into(box: Box[Animal]): ...

   my_box = Box(Cat())
   look_into(my_box)  # OK, but mypy would complain here for an invariant type

.. _type-variable-upper-bound:

Type variables with upper bounds
********************************

A type variable can also be restricted to having values that are
subtypes of a specific type. This type is called the upper bound of
the type variable, and is specified with the ``bound=...`` keyword
argument to :py:class:`~typing.TypeVar`.

.. code-block:: python

   from typing import TypeVar, SupportsAbs

   T = TypeVar('T', bound=SupportsAbs[float])

In the definition of a generic function that uses such a type variable
``T``, the type represented by ``T`` is assumed to be a subtype of
its upper bound, so the function can use methods of the upper bound on
values of type ``T``.

.. code-block:: python

   def largest_in_absolute_value(*xs: T) -> T:
       return max(xs, key=abs)  # Okay, because T is a subtype of SupportsAbs[float].

In a call to such a function, the type ``T`` must be replaced by a
type that is a subtype of its upper bound. Continuing the example
above:

.. code-block:: python

   largest_in_absolute_value(-3.5, 2)   # Okay, has type float.
   largest_in_absolute_value(5+6j, 7)   # Okay, has type complex.
   largest_in_absolute_value('a', 'b')  # Error: 'str' is not a subtype of SupportsAbs[float].

Type parameters of generic classes may also have upper bounds, which
restrict the valid values for the type parameter in the same way.

.. _type-variable-value-restriction:

Type variables with value restriction
*************************************

By default, a type variable can be replaced with any type. However, sometimes
it's useful to have a type variable that can only have some specific types
as its value. A typical example is a type variable that can only have values
``str`` and ``bytes``:

.. code-block:: python

   from typing import TypeVar

   AnyStr = TypeVar('AnyStr', str, bytes)

This is actually such a common type variable that :py:data:`~typing.AnyStr` is
defined in :py:mod:`typing` and we don't need to define it ourselves.

We can use :py:data:`~typing.AnyStr` to define a function that can concatenate
two strings or bytes objects, but it can't be called with other
argument types:

.. code-block:: python

   from typing import AnyStr

   def concat(x: AnyStr, y: AnyStr) -> AnyStr:
       return x + y

   concat('a', 'b')    # Okay
   concat(b'a', b'b')  # Okay
   concat(1, 2)        # Error!

Importantly, this is different from a union type, since combinations
of ``str`` and ``bytes`` are not accepted:

.. code-block:: python

   concat('string', b'bytes')   # Error!

In this case, this is exactly what we want, since it's not possible
to concatenate a string and a bytes object! If we tried to use
``Union``, the type checker would complain about this possibility:

.. code-block:: python

   def union_concat(x: Union[str, bytes], y: Union[str, bytes]) -> Union[str, bytes]:
       return x + y  # Error: can't concatenate str and bytes

Another interesting special case is calling ``concat()`` with a
subtype of ``str``:

.. code-block:: python

    class S(str): pass

    ss = concat(S('foo'), S('bar'))
    reveal_type(ss)  # Revealed type is "builtins.str"

You may expect that the type of ``ss`` is ``S``, but the type is
actually ``str``: a subtype gets promoted to one of the valid values
for the type variable, which in this case is ``str``.

This is thus
subtly different from *bounded quantification* in languages such as
Java, where the return type would be ``S``. The way mypy implements
this is correct for ``concat``, since ``concat`` actually returns a
``str`` instance in the above example:

.. code-block:: python

    >>> print(type(ss))
    <class 'str'>

You can also use a :py:class:`~typing.TypeVar` with a restricted set of possible
values when defining a generic class. For example, mypy uses the type
:py:class:`Pattern[AnyStr] <typing.Pattern>` for the return value of :py:func:`re.compile`,
since regular expressions can be based on a string or a bytes pattern.

A type variable may not have both a value restriction (see
:ref:`type-variable-upper-bound`) and an upper bound.

.. _declaring-decorators:

Declaring decorators
********************

Decorators are typically functions that take a function as an argument and
return another function. Describing this behaviour in terms of types can
be a little tricky; we'll show how you can use ``TypeVar`` and a special
kind of type variable called a *parameter specification* to do so.

Suppose we have the following decorator, not type annotated yet,
that preserves the original function's signature and merely prints the decorated function's name:

.. code-block:: python

   def printing_decorator(func):
       def wrapper(*args, **kwds):
           print("Calling", func)
           return func(*args, **kwds)
       return wrapper

and we use it to decorate function ``add_forty_two``:

.. code-block:: python

   # A decorated function.
   @printing_decorator
   def add_forty_two(value: int) -> int:
       return value + 42

   a = add_forty_two(3)

Since ``printing_decorator`` is not type-annotated, the following won't get type checked:

.. code-block:: python

   reveal_type(a)        # Revealed type is "Any"
   add_forty_two('foo')  # No type checker error :(

This is a sorry state of affairs! If you run with ``--strict``, mypy will
even alert you to this fact:
``Untyped decorator makes function "add_forty_two" untyped``

Note that class decorators are handled differently than function decorators in
mypy: decorating a class does not erase its type, even if the decorator has
incomplete type annotations.

Here's how one could annotate the decorator:

.. code-block:: python

   from typing import Any, Callable, TypeVar, cast

   F = TypeVar('F', bound=Callable[..., Any])

   # A decorator that preserves the signature.
   def printing_decorator(func: F) -> F:
       def wrapper(*args, **kwds):
           print("Calling", func)
           return func(*args, **kwds)
       return cast(F, wrapper)

   @printing_decorator
   def add_forty_two(value: int) -> int:
       return value + 42

   a = add_forty_two(3)
   reveal_type(a)      # Revealed type is "builtins.int"
   add_forty_two('x')  # Argument 1 to "add_forty_two" has incompatible type "str"; expected "int"

This still has some shortcomings. First, we need to use the unsafe
:py:func:`~typing.cast` to convince mypy that ``wrapper()`` has the same
signature as ``func``. See :ref:`casts <casts>`.

Second, the ``wrapper()`` function is not tightly type checked, although
wrapper functions are typically small enough that this is not a big
problem. This is also the reason for the :py:func:`~typing.cast` call in the
``return`` statement in ``printing_decorator()``.

However, we can use a parameter specification (:py:class:`~typing.ParamSpec`),
for a more faithful type annotation:

.. code-block:: python

   from typing import Callable, TypeVar
   from typing_extensions import ParamSpec

   P = ParamSpec('P')
   T = TypeVar('T')

   def printing_decorator(func: Callable[P, T]) -> Callable[P, T]:
       def wrapper(*args: P.args, **kwds: P.kwargs) -> T:
           print("Calling", func)
           return func(*args, **kwds)
       return wrapper

Parameter specifications also allow you to describe decorators that
alter the signature of the input function:

.. code-block:: python

   from typing import Callable, TypeVar
   from typing_extensions import ParamSpec

   P = ParamSpec('P')
   T = TypeVar('T')

    # We reuse 'P' in the return type, but replace 'T' with 'str'
   def stringify(func: Callable[P, T]) -> Callable[P, str]:
       def wrapper(*args: P.args, **kwds: P.kwargs) -> str:
           return str(func(*args, **kwds))
       return wrapper

    @stringify
    def add_forty_two(value: int) -> int:
        return value + 42

    a = add_forty_two(3)
    reveal_type(a)      # Revealed type is "builtins.str"
    add_forty_two('x')  # error: Argument 1 to "add_forty_two" has incompatible type "str"; expected "int"

Or insert an argument:

.. code-block:: python

    from typing import Callable, TypeVar
    from typing_extensions import Concatenate, ParamSpec

    P = ParamSpec('P')
    T = TypeVar('T')

    def printing_decorator(func: Callable[P, T]) -> Callable[Concatenate[str, P], T]:
        def wrapper(msg: str, /, *args: P.args, **kwds: P.kwargs) -> T:
            print("Calling", func, "with", msg)
            return func(*args, **kwds)
        return wrapper

    @printing_decorator
    def add_forty_two(value: int) -> int:
        return value + 42

    a = add_forty_two('three', 3)

.. _decorator-factories:

Decorator factories
-------------------

Functions that take arguments and return a decorator (also called second-order decorators), are
similarly supported via generics:

.. code-block:: python

    from typing import Any, Callable, TypeVar

    F = TypeVar('F', bound=Callable[..., Any])

    def route(url: str) -> Callable[[F], F]:
        ...

    @route(url='/')
    def index(request: Any) -> str:
        return 'Hello world'

Sometimes the same decorator supports both bare calls and calls with arguments. This can be
achieved by combining with :py:func:`@overload <typing.overload>`:

.. code-block:: python

    from typing import Any, Callable, Optional, TypeVar, overload

    F = TypeVar('F', bound=Callable[..., Any])

    # Bare decorator usage
    @overload
    def atomic(__func: F) -> F: ...
    # Decorator with arguments
    @overload
    def atomic(*, savepoint: bool = True) -> Callable[[F], F]: ...

    # Implementation
    def atomic(__func: Optional[Callable[..., Any]] = None, *, savepoint: bool = True):
        def decorator(func: Callable[..., Any]):
            ...  # Code goes here
        if __func is not None:
            return decorator(__func)
        else:
            return decorator

    # Usage
    @atomic
    def func1() -> None: ...

    @atomic(savepoint=False)
    def func2() -> None: ...

Generic protocols
*****************

Mypy supports generic protocols (see also :ref:`protocol-types`). Several
:ref:`predefined protocols <predefined_protocols>` are generic, such as
:py:class:`Iterable[T] <typing.Iterable>`, and you can define additional generic protocols. Generic
protocols mostly follow the normal rules for generic classes. Example:

.. code-block:: python

   from typing import TypeVar
   from typing_extensions import Protocol

   T = TypeVar('T')

   class Box(Protocol[T]):
       content: T

   def do_stuff(one: Box[str], other: Box[bytes]) -> None:
       ...

   class StringWrapper:
       def __init__(self, content: str) -> None:
           self.content = content

   class BytesWrapper:
       def __init__(self, content: bytes) -> None:
           self.content = content

   do_stuff(StringWrapper('one'), BytesWrapper(b'other'))  # OK

   x: Box[float] = ...
   y: Box[int] = ...
   x = y  # Error -- Box is invariant

Note that ``class ClassName(Protocol[T])`` is allowed as a shorthand for
``class ClassName(Protocol, Generic[T])``, as per :pep:`PEP 544: Generic protocols <544#generic-protocols>`,

The main difference between generic protocols and ordinary generic
classes is that mypy checks that the declared variances of generic
type variables in a protocol match how they are used in the protocol
definition.  The protocol in this example is rejected, since the type
variable ``T`` is used covariantly as a return type, but the type
variable is invariant:

.. code-block:: python

   from typing import Protocol, TypeVar

   T = TypeVar('T')

   class ReadOnlyBox(Protocol[T]):  # error: Invariant type variable "T" used in protocol where covariant one is expected
       def content(self) -> T: ...

This example correctly uses a covariant type variable:

.. code-block:: python

   from typing import Protocol, TypeVar

   T_co = TypeVar('T_co', covariant=True)

   class ReadOnlyBox(Protocol[T_co]):  # OK
       def content(self) -> T_co: ...

   ax: ReadOnlyBox[float] = ...
   ay: ReadOnlyBox[int] = ...
   ax = ay  # OK -- ReadOnlyBox is covariant

See :ref:`variance-of-generics` for more about variance.

Generic protocols can also be recursive. Example:

.. code-block:: python

   T = TypeVar('T')

   class Linked(Protocol[T]):
       val: T
       def next(self) -> 'Linked[T]': ...

   class L:
       val: int
       def next(self) -> 'L': ...

   def last(seq: Linked[T]) -> T: ...

   result = last(L())
   reveal_type(result)  # Revealed type is "builtins.int"

.. _generic-type-aliases:

Generic type aliases
********************

Type aliases can be generic. In this case they can be used in two ways:
Subscripted aliases are equivalent to original types with substituted type
variables, so the number of type arguments must match the number of free type variables
in the generic type alias. Unsubscripted aliases are treated as original types with free
variables replaced with ``Any``. Examples (following :pep:`PEP 484: Type aliases
<484#type-aliases>`):

.. code-block:: python

    from typing import TypeVar, Iterable, Union, Callable

    S = TypeVar('S')

    TInt = tuple[int, S]
    UInt = Union[S, int]
    CBack = Callable[..., S]

    def response(query: str) -> UInt[str]:  # Same as Union[str, int]
        ...
    def activate(cb: CBack[S]) -> S:        # Same as Callable[..., S]
        ...
    table_entry: TInt  # Same as tuple[int, Any]

    T = TypeVar('T', int, float, complex)

    Vec = Iterable[tuple[T, T]]

    def inproduct(v: Vec[T]) -> T:
        return sum(x*y for x, y in v)

    def dilate(v: Vec[T], scale: T) -> Vec[T]:
        return ((x * scale, y * scale) for x, y in v)

    v1: Vec[int] = []      # Same as Iterable[tuple[int, int]]
    v2: Vec = []           # Same as Iterable[tuple[Any, Any]]
    v3: Vec[int, int] = [] # Error: Invalid alias, too many type arguments!

Type aliases can be imported from modules just like other names. An
alias can also target another alias, although building complex chains
of aliases is not recommended -- this impedes code readability, thus
defeating the purpose of using aliases.  Example:

.. code-block:: python

    from typing import TypeVar, Generic, Optional
    from example1 import AliasType
    from example2 import Vec

    # AliasType and Vec are type aliases (Vec as defined above)

    def fun() -> AliasType:
        ...

    T = TypeVar('T')

    class NewVec(Vec[T]):
        ...

    for i, j in NewVec[int]():
        ...

    OIntVec = Optional[Vec[int]]

Using type variable bounds or values in generic aliases has the same effect
as in generic classes/functions.


Generic class internals
***********************

You may wonder what happens at runtime when you index a generic class.
Indexing returns a *generic alias* to the original class that returns instances
of the original class on instantiation:

.. code-block:: python

   >>> from typing import TypeVar, Generic
   >>> T = TypeVar('T')
   >>> class Stack(Generic[T]): ...
   >>> Stack
   __main__.Stack
   >>> Stack[int]
   __main__.Stack[int]
   >>> instance = Stack[int]()
   >>> instance.__class__
   __main__.Stack

Generic aliases can be instantiated or subclassed, similar to real
classes, but the above examples illustrate that type variables are
erased at runtime. Generic ``Stack`` instances are just ordinary
Python objects, and they have no extra runtime overhead or magic due
to being generic, other than a metaclass that overloads the indexing
operator.

Note that in Python 3.8 and lower, the built-in types
:py:class:`list`, :py:class:`dict` and others do not support indexing.
This is why we have the aliases :py:class:`~typing.List`,
:py:class:`~typing.Dict` and so on in the :py:mod:`typing`
module. Indexing these aliases gives you a generic alias that
resembles generic aliases constructed by directly indexing the target
class in more recent versions of Python:

.. code-block:: python

   >>> # Only relevant for Python 3.8 and below
   >>> # For Python 3.9 onwards, prefer `list[int]` syntax
   >>> from typing import List
   >>> List[int]
   typing.List[int]

Note that the generic aliases in ``typing`` don't support constructing
instances:

.. code-block:: python

   >>> from typing import List
   >>> List[int]()
   Traceback (most recent call last):
   ...
   TypeError: Type List cannot be instantiated; use list() instead
