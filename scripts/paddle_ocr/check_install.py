import paddle

paddle.utils.run_check()

# f:\dev\python\.venv\Lib\site-packages\paddle\utils\cpp_extension\extension_utils.py:711: UserWarning: No ccache found. Please be aware that recompiling all source files may be required. You can download and install ccache from: https://github.com/ccache/ccache/blob/master/doc/INSTALL.md
#   warnings.warn(warning_message)
# Running verify PaddlePaddle program ... 
# I0508 18:52:02.395442 57328 pir_interpreter.cc:1541] New Executor is Running ...
# W0508 18:52:02.395442 57328 gpu_resources.cc:119] Please NOTE: device: 0, GPU Compute Capability: 8.6, Driver API Version: 12.7, Runtime API Version: 12.6
# W0508 18:52:02.396443 57328 gpu_resources.cc:164] device: 0, cuDNN Version: 9.5.
# I0508 18:52:02.398952 57328 pir_interpreter.cc:1564] pir interpreter is running by multi-thread mode ...
# PaddlePaddle works well on 1 GPU.
# PaddlePaddle is installed successfully! Let's start deep learning with PaddlePaddle now.