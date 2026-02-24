from aio.utils import get_from_tg_table


async def test_run_sql(session):
    res = await get_from_tg_table(session)
    assert isinstance(res, list)
