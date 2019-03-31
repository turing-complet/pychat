import pytest
from libchat import Message

def test_message_serialize():
    m1 = Message(b'alice', b'/join')
    m2 = Message(b'bob', message=b'hi alice')

    b1 = m1.as_bytes()
    b2 = m2.as_bytes()
    print(b1)
    print(b2)
    assert 1==1