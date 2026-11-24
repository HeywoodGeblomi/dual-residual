# Exploratory clean-room differential harness. Does not modify the core.
CXX := g++
CXXFLAGS := -std=c++17 -O2 -Wall -Wextra
LDFLAGS :=

JOB4 := /workspace/toni/dual-residual-job4
HERE := $(JOB4)/cleanroom_diff
SRC_IO := $(JOB4)/src
CORE := $(JOB4)/core
BIN := $(HERE)/bin
OBJ := $(HERE)/obj

.PHONY: all clean

all: $(BIN)/core_dump

$(BIN) $(OBJ):
	mkdir -p $(BIN) $(OBJ)

$(OBJ)/ds1_io.o: $(SRC_IO)/ds1_io.cpp $(SRC_IO)/ds1_io.hpp | $(OBJ)
	$(CXX) $(CXXFLAGS) -I$(SRC_IO) -c $< -o $@

$(BIN)/core_dump: $(HERE)/src/core_dump.cpp $(OBJ)/ds1_io.o $(CORE)/dual_residual.hpp $(CORE)/dual_residual_prod.hpp | $(BIN)
	$(CXX) $(CXXFLAGS) -I$(SRC_IO) -I$(CORE) $(HERE)/src/core_dump.cpp $(OBJ)/ds1_io.o -o $@ $(LDFLAGS)

clean:
	rm -f $(OBJ)/ds1_io.o $(BIN)/core_dump
