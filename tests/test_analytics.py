from product_service.analytics import ProductAnalytics


def test_compute_avg_from_list_nonempty():
    products = [{"price": 10}, {"price": 20}, {"price": 30}]
    avg = ProductAnalytics.compute_avg_from_list(products)
    assert abs(avg - 20.0) < 1e-6


def test_compute_avg_from_list_empty():
    avg = ProductAnalytics.compute_avg_from_list([])
    assert avg == 0.0