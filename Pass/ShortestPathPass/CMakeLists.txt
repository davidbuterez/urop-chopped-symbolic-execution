add_llvm_loadable_module(LLVMShortestPathPass
  ShortestPathPass.cpp
  )

SET(CMAKE_CXX_FLAGS "-Wall -std=c++11 -fno-rtti")