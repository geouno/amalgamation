#pragma once
// test_result.hpp amalgamation

#include <numeric>
#include <queue>
#include <string>
#include <vector>

#include "no_expand.hpp"

// i1.hpp
// i1 linebreak
class c1 {
public:
	static int m1;
	int m2();
};

// i2.hpp
// i2 linebreak
// i2 linebreak
// i2 linebreak
class c2 {
public:
	std::vector<c1> m1;
	int m2() {
		return m1.size();
	};
};

// i3.hpp
// i3 linebreak
// i3 linebreak
// i3 linebreak
class c3 {
public:
	std::queue<c1> m1;
	int m2() {
		return m1.size();
	};
};

// i4.hpp
// i4 linebreak
// i4 linebreak
class c4 {
public:
	std::pair<c2, c3> m1;
	int m2() {
		return m1.first.m2() + m1.second.m2();
	};
};

// arc.h
#ifndef SOME_INCLUDE_GUARD
#define SOME_INCLUDE_GUARD

std::string some_string = "hello\
#include <world>\
";

/*
#include <something>

#include "another"
*/
// #include "third"

#endif
