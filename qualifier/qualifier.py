import typing
from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    scope: typing.Mapping[str, typing.Any]

    receive: typing.Callable[[], typing.Awaitable[object]]
    send: typing.Callable[[object], typing.Awaitable[None]]


class RestaurantManager:
    def __init__(self):
        """Instantiate the restaurant manager.

        This is called at the start of each day before any staff get on
        duty or any orders come in. You should do any setup necessary
        to get the system working before the day starts here; we have
        already defined a staff dictionary.
        """
        self.staff = {}
        self.freq = {}

    async def __call__(self, request: Request):
        """Handle a request received.

        This is called for each request received by your application.
        In here is where most of the code for your system should go.

        :param request: request object
            Request object containing information about the sent
            request to your application.
        """
        if request.scope['type'] == 'staff.onduty':
            self.staff[request.scope['id']] = request
            self.freq[request.scope['id']] = 0
        
        if request.scope['type'] == 'staff.offduty':
            del self.staff[request.scope['id']]
            del self.freq[request.scope['id']]

        if request.scope['type'] == 'order':
            spec = request.scope['speciality']
            poss = []
            for staff_id in self.staff:
                if spec in self.staff[staff_id].scope['speciality']:
                    poss.append(staff_id)
            id_chosen = min(poss, key = lambda id:self.freq[id])
            staff_chosen = self.staff[id_chosen]
            self.freq[id_chosen] += 1
            full_order = await request.receive()
            await staff_chosen.send(full_order)
            res = await staff_chosen.receive()
            await request.send(res)
