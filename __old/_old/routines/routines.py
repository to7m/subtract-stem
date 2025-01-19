


def make_signature(
    *, required_positional={}, required_keyword={}, optional_keyword={}
):
    return Node()


class Signature(NodeBase):
    def __init__(
        self, *,
        required_positional={}, required_keyword={}, optional_keyword={}
    ):
        self.routines_factory_cls = +...

        self.all_args = {}
        self.required_positional = self._handle_args(required_positional)
        self.required_keyword = self._handle_args(required_keyword)
        self.optional_keyword = self._handle_args(optional_keyword)

    def _handle_args(self, args):
        if type(args) is not dict:
            raise TypeError(
                "all arguments passed to Signature should be dicts"
            )

        for arg_name, param in args.items():
            if type(arg_name) is not str:
                raise TypeError(
                    "all keys in dicts passed to Signature should be str "
                    "instances"
                )

            if arg_name in self.all_args:
                raise RuntimeError(
                    f"argument name {arg_name!r} provided multiple times"
                )

            check param

            self.all_args[arg_name] = param

        return args


class TupleNode(NodeBase):
    def __init__(self, *nodes):
        self._nodes = tuple(self._verify_node(node) for node in nodes)



class Mul(RoutinesDef):
    class MulNode(NodeBase):
        def __init__(self):
            self.prev_nodes = []

    @classmethod
    def new_node(self, a, b):
        if a

        return MulNode()

    def 



class Node:
    pass



class RoutineDef:
    def __init__(self, *, make_routines):
        self.make_routines = make_routines
        self.make_partial = make_partial


class CompositeRoutineDefConstructor:
    def __init__(self):
        ...

    def set_signature(
        self, *,
        positional_required={}, keyword_required={}, keyword_optional={}
    ):
        ...

    def set_return(self, ret):
        ...

    def make_routine_def(self):
        def make_routine(*xargs, **kwargs):
            if xargs or kwargs:
                return self.make_routine_def().make_partial(*xargs, **kwargs)

            construction_args \
                = self.signature.verify_and_format_args(
                      *xargs, **kwargs
                  )

            resources = []
            resources += ([arg] for arg in construction_args.values())
            resources += ([None] for _ in self.runtime_signature)

            for subroutine_def in self._subroutine_calls:
                subroutine_def.make_routine()



            main_resources = 

            def main_routine(*xargs, **kwargs):
                verify_main_routine_args(xargs, kwargs)

                for routine in main_subroutines:
                    routine()

        def make_partial(*xargs, **kwargs):
            ...

        return RoutinesDef(make_routines=make_routines)


crdc = CompositeRoutineDefConstructor()
args = crdc.set_signature(positional_required={"a": ArrayParam()})
b = crdc.append(mul, rargs.a, 7)
c = crdc.append(add, b, rargs.a)
d = crdc.append(mul, b, rargs.a)
e = crdc.append(add, c, d)
crdc.set_return((d, e))
whatever_this_does = crdc.make_routine_def()

routine = whatever_this_does.make_routine()
for _ in range(num_of_iterations):
    result = routine(np.array[1, 2, 3])











class Signature:
    def __init__(
        self, *,
        required_positional={}, required_keyword={}, optional_keyword={}
    ):
        (
            self.required_positional,
            self.required_keyword,
            self.optional_keyword
        ) = sanitise_args(
            "required_positional", "required_keyword", "optional_keyword"
        )





class Resources:
    def __init__(self, *, _data=None):
        if _data is None:
            self._data = []
        else:
            self._data = _data

    def __getitem__(self, i):
        if type(i) is int:
            return self._data[i][0]
        else:
            raise TypeError(
                f"{i} is an invalid index for a Resources instance"
            )

    def __setitem__(self, i, val):
        if type(i) is int:
            self._data[i][0] = val
        else:
            raise TypeError(
                f"{i} is an invalid index for a Resources instance"
            )

    def append(self, val):
        self._data.append([val])


class GraphDef:
    def __init__(self, *, num_of_before_iterations, num_of_main_iterations):
        (
            self.num_of_before_iterations, self.num_of_main_iterations
        ) = sanitise_args(
            "num_of_before_iterations", "num_of_main_iterations"
        )

        self.resource_factories = Resources.new()
        self.routines_factories = []

    def __call__(self):
        before_routines, main_routines = [], []

        for routines_factory in routines_factories:
            routines = routines_factory()

            if "before_routine" in routines:
                before_routines.append(routines["before_routine"])

            if "main_routine" in routines:
                main_routines.append(routines["main_routine"])

        routines = {}

        if before_routines:
            def before_routine():
                for routine in before_routines:
                    routine()

            routines["before_routine"] = before_routine

        if main_routines:
            def main_routine():
                for routine in main_routines:
                    routine()

            routines["main_routine"] = main_routine

        return routines

    def append_resource_factory(self, resource_factory):
        self.resource_factories.append(resource_factory)

    def append_resource(self, resource):
        self.resource_factories(append(lambda: resource))

    def append_routine_factory(
        self, routine_factory, *,
        allow_missing_info=False, allow_wrong_info=False
    ):
        info = {}
        for stage in ["before", "after"]:
            attr_name = f"num_of_{stage}_iterations"

            if hasattr(routine_factory, attr_name):
                info[attr_name] = val = getattr(routine_factory, attr_name)
            elif allow_missing_info:
                info[attr_name] = getattr(self, attr_name)
            else:
                raise AttributeError(
                    f"routine_factory has no attribute {attr_name!r}"
                )

        sanitise_args(**info)

        if not allow_wrong_info:
            for attr_name, val in info.items():
                self_val = getattr(self, attr_name)

                if val != self_val:
                    raise RuntimeError(
                        f"routine_factory value for attribute {attr_name!r} "
                        f"({val}) should be the same as GraphDef instance's "
                        f"value ({self_val})"
                    )

        self.routine_factories.append(routine_factory)




    def __iter__(self):
        for iteration_i, num_of_iterations in self.iterate_before():
            yield "before iterations", iteration_i, num_of_iterations

        for iteration_i, num_of_iterations in self.iterate_main():
            yield "main iterations", iteration_i, num_of_iterations

    def append_resource(self, resource):
        resource_i = len(self.resources)

        self.resources.append(resource)

        return resource_i

    def append_before_routine(self, routine):
        if hasattr(routine, "num_of_before_iterations"):
            if routine.num_of_before_iterations != self.num_of_before_iterations

        self.before_routines.append(routine)

    def append_main_routine(self, routine):
        self.main_routines.append(routine)

    def get_before_routine(self):
        routines = self.before_routines

        def routine(i):
            for routine in routines:
                routine(i)

        return routine

    def get_main_routine(self):
        routines = self.main_routines

        def routine(i):
            for routine in routines:
                routine(i)

        return routine

    def iterate_before(self):
        num_of_iterations = self.num_of_before_iterations
        routines = self.before_routines

        if num_of_iterations == 0:
            return

        for i in range(num_of_iterations):
            yield i, num_of_iterations

            for routine in routines:
                routine(i)

        yield num_of_iterations, num_of_iterations

    def iterate_main(self):
        num_of_iterations = self.num_of_main_iterations
        routines = self.main_routines

        if num_of_iterations == 0:
            return

        for i in range(num_of_iterations):
            yield i, num_of_iterations

            for routine in routines(i):
                routine(i)

        yield num_of_iterations, num_of_iterations

    def run_before_iterations(self):
        for _ in self.iterate_before():
            pass

    def run_main_iterations(self):
        for _ in self.iterate_main():
            pass

    def run(self):
        self.run_before_iterations()
        self.run_main_iterations()
