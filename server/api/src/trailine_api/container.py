from dependency_injector import containers

class Container(containers):
    wiring_config = containers.WiringConfiguration(
        modules=[]
    )
