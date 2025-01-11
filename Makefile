# Compiler
CXX = g++

# wxWidgets flags
WX_CFLAGS = `wx-config --cxxflags`
WX_LDFLAGS = `wx-config --libs`

# Compiler flags
CXXFLAGS = -std=c++11 $(WX_CFLAGS)

# Linker flags
LDFLAGS = $(WX_LDFLAGS)

# Source files
SRCS = main.cpp

# Output executable
TARGET = game_launcher_wx

# Default target
all: $(TARGET)

# Build the target for wxWidgets application
$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRCS) $(LDFLAGS)

# Clean up build files
clean:
	rm -f $(TARGET)

# Phony targets
.PHONY: all clean
