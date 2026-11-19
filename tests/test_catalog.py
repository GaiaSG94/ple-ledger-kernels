from harness.kernels import KERNELS, catalog, run


def test_catalog_covers_every_kernel():
    names = [entry["name"] for entry in catalog()]
    assert names == list(KERNELS)
    for entry in catalog():
        assert entry["summary"], entry["name"]
        assert entry["params"], entry["name"]


def test_catalog_lists_arguments_of_a_kernel():
    by_name = {entry["name"]: entry for entry in catalog()}
    assert by_name["cable-size"]["params"] == [
        "I", "L", "V", "system", "material", "max_drop_pct",
    ]
    assert by_name["mna-ac"]["params"] == ["freq_hz", "elements", "probe_nodes"]


def test_every_kernel_is_registered():
    # One callable per name, no dead entries.
    for name, fn in KERNELS.items():
        assert callable(fn), name
        assert fn.__doc__, name
    assert len(set(KERNELS)) == len(KERNELS)
    assert callable(run)
