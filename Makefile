test:
	python setup.py test -a "--cov-config .coveragerc --cov=beacon"

generate_grpc_client:
	pipenv run python -m grpc_tools.protoc --proto_path=../contracts --python_out=beacon --grpc_python_out=beacon ../contracts/beacon.proto
