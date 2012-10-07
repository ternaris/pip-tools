import unittest
from piptools.datastructures import SpecSet
from piptools.package_manager import FakePackageManager


def print_specset(specset, round):
    print('After round #%s:' % (round,))
    for spec in specset:
        print('  - %s' % (spec.description(),))


simple = {
    'foo-0.1': ['bar'],
    'bar-1.2': ['qux', 'simplejson'],
    'qux-0.1': ['simplejson<2.6'],

    'simplejson-2.4.0': [],
    'simplejson-2.6.2': [],
}


class TestDependencyResolving(unittest.TestCase):
    def test_find_dependencies_simple(self):
        """A simple scenario for finding dependencies."""
        pkgmgr = FakePackageManager(simple)

        spec_set = SpecSet()
        spec_set.add_spec('foo')

        round = 1
        print_specset(spec_set, round)
        while True:
            round += 1
            new_deps = []
            for spec in spec_set.normalize():
                version = pkgmgr.find_best_match(spec)
                pkg_deps = pkgmgr.get_dependencies(spec.name, version)

                # Append source information to the new specs
                if spec.source:
                    source = '%s ~> %s==%s' % (spec.source, spec.name, version)
                else:
                    source = '%s==%s' % (spec.name, version)
                pkg_deps = [s.add_source(source) for s in pkg_deps]
                new_deps += pkg_deps

            if not new_deps:
                break

            # TODO: We should detect whether adding the new_deps really
            # "changes anything" to the spec set.  In order words: if no
            # significant new constraints are added, we're done

            # XXX: FIXME: Current, we "just stop" after X rounds (to prevent
            # endless loops), but obviously this is not the correct impl!
            if round > 4:
                break

            spec_set.add_specs(new_deps)
            print_specset(spec_set, round)

        # Print the final result:
        print_specset(spec_set.normalize(), 'final')

        spec_set = spec_set.normalize()
        self.assertItemsEqual(['foo', 'qux', 'bar', 'simplejson<2.6'], map(str, spec_set))