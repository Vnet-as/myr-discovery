
from myr.discovery import announce, discover


def test_announce():
    tasks = {
        'myr.billstack.something': {
            'signature': {},
            'routing': {'queue': 'billstack'},
        },
        'myr.invoicing.something': {
            'signature': {},
            'routing': {'queue': 'invoicing'},
        }
    }
    announce(tasks)
    discovered_tasks = discover()
    assert tasks == discovered_tasks
