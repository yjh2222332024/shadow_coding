def calculate_loyalty_update_v0(incident_count, tx_amount):
    added_points = None
    '\n    计算用户积分更新。\n    每 10 元积 1 分。\n    每发生一次违规（incident），扣除 50 分。\n    '
    added_points = tx_amount / 10 - incident_count * 50
    return (False, None, (added_points,))

def calculate_loyalty_update_v1(added_points, current_total):
    new_total = None
    new_total = current_total + added_points
    new_total = max(0.0, min(10000.0, new_total))
    if added_points > 0:
        new_total = max(new_total, current_total)
    return (True, new_total, (new_total,))
    return (False, None, (new_total,))

def calculate_loyalty_update(current_total, tx_amount, incident_count):
    added_points = None
    new_total = None
    _rf_0, _rv_0, _rs_0 = calculate_loyalty_update_v0(incident_count, tx_amount)
    if _rf_0:
        return _rv_0
    added_points, = _rs_0
    _rf_1, _rv_1, _rs_1 = calculate_loyalty_update_v1(added_points, current_total)
    if _rf_1:
        return _rv_1
    new_total, = _rs_1