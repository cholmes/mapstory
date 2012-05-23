from watchdog.core import check
from watchdog.core import check_many
from watchdog.core import subcheck


def suite():
    return (
        test_single,
        test_single_fail,
        test_many,
        test_restart
    )


@check
def test_single():
    print 'test_single'


@check
def test_single_fail():
    print 'test_single_fail'
    raise Exception('dang')


@check_many
def test_many():
    print 'test_many'

    def test(i):
        print 'test_many %s' % i

    for i in range(5):
        yield subcheck(test, 'subtest', i)


@check(restart_on_error=True)
def test_restart():
    print 'test_restart'
    raise Exception('failure')
