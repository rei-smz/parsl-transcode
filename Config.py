from parsl.config import Config
from parsl.executors import HighThroughputExecutor
from parsl.providers import KubernetesProvider
from parsl.addresses import address_by_route

transcode_config = Config(
    executors=[
        HighThroughputExecutor(
            label='kube-htex',
            max_workers_per_node=1,
            worker_logdir_root='/app',

            # Address for the pod worker to connect back
            address=address_by_route(),
            provider=KubernetesProvider(
                namespace="parsl-transcode",

                # Docker image url to use for pods
                image='YOUR_DOCKER_URL',

                # Command to be run upon pod start, such as:
                # 'module load Anaconda; source activate parsl_env'.
                # or 'pip install parsl'
                worker_init='',

                # The secret key to download the image
                secret="YOUR_KUBE_SECRET",

                # Should follow the Kubernetes naming rules
                pod_name='parsl-transcode-pod',

                nodes_per_block=1,
                init_blocks=1,
                # Maximum number of pods to scale up
                max_blocks=10,
                max_cpu=10,
                max_mem="1024Mi",
                init_mem="512Mi",
                init_cpu=8
            ),
        ),
    ]
)
