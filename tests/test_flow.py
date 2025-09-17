from dispatcher.flow import DispatcherFlow

def test_dispatcher_flow():
    flow = DispatcherFlow()
    assert flow.input_data is None

    flow.load_data('tests/input.csv')
    assert flow.input_data is not None
    assert not flow.input_data.empty

    flow.run_sorting()

    flow.show_statistics()
    print("Test completed successfully")