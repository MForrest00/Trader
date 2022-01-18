from trader.tasks import app


@app.task
def handle_buy_signal(buy_signal_id: int) -> None:
    pass
