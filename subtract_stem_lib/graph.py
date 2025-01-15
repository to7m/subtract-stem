class Resources:
    def __init__(self, *, _data):
        self._data = _data

    def __getitem__(self, i):
        return self._data[i][0]

    def __setitem__(self, i, val):
        self._data[i][0] = val

    def append(self, val):
        self._data.append([val])

    @classmethod
    def new_empty(cls):
        return cls([])


class GraphDef:
    def __init__(self, *, num_of_before_iterations, num_of_main_iterations):
        self.num_of_before_iterations \
            = self._sanitise_num_of_before_iterations(
                  num_of_before_iterations
              )
        self.num_of_main_iterations = num_of_main_iterations
        self.resource_factories = _Resources()
        self.routine_factories = []

    def _check_num_of_before_iterations(self, num_of_before_iterations):
        if type(num_of_before_iterations) is not int:
            raise TypeError("num_of_before_iterations should be an int")

        if self.num_of_before_iterations is None:

    def append_resource_factory(self, resource_factory):
        self.resource_factories.append(resource_factory)

    def append_resource(self, resource):
        self.resource_factories(append(lambda: resource))

    def append_routine_factory(
        self, routine_factory, *,
        allow_missing_info=False, allow_wrong_info=False
    ):
        if hasattr(routine_factory, "num_of_before_iterations"):
            self._check_num_of_before_iterations(
                routine_factory.num_of_before_iterations
            )

        self.routine_factories.append(routine_factory)

    def append_routine(self, main_routine, *, before_routine=None):
        def routine_factory():
            return {
                "before_routine": before_routine,
                "main_routine": main_routine
            }

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
