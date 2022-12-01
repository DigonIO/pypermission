===========
Persistency
===========

JSON File
=========

Save data to a JSON file
------------------------

.. code-block:: python

    from pypermission.json import Authority

    DATA_FILE = "<data_file_path>.json"  # pathlib.Path | str

    auth = Authority(data_file=DATA_FILE)

    # do userful stuff

    auth.save_to_file()

Load data from a JSON file
--------------------------

.. code-block:: python

    from pypermission.json import Authority

    DATA_FILE = "<data_file_path>.json"  # pathlib.Path | str

    auth = Authority(data_file=DATA_FILE)

    # do userful stuff

    auth.load_from_file()

JSON String
===========

Save data to a JSON string
--------------------------

.. code-block:: python

    from pypermission.json import Authority

    auth = Authority()

    # do userful stuff

    serial_data: str = auth.save_to_str()

Load data from a JSON string
----------------------------

.. code-block:: python

    from pypermission.json import Authority

    auth = Authority()

    # do userful stuff

    # NOTE the serial data has to be loaded, e.g. from a file
    auth.load_from_str(serial_data=serial_data)
