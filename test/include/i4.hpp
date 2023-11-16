#pragma once
// i4 linebreak
#include "i2.hpp"
#include "i3.hpp"
// i4 linebreak
class c4 {
public:
	std::pair<c2, c3> m1;
	int m2() {
		return m1.first.m2() + m1.second.m2();
	};
};
