#!/usr/bin/env python3

import argparse
import os
import re
import sys
from typing import List



class DPP(object):
	# path: 			str 			path to file
	# name: 			str 			display name of file
	# includes(): 		List[str]		includes
	# content(): 		str 			parsed content (w/o includes)

	def __init__(self, path: str, name: str) -> None:
		self.path: str = os.path.abspath(path)
		self.name: str = name

		self._content: str | None = None
		self._skippable_contexts: List | None = None
		self._includes: List[str] | None = None

		# parse() helper variables
		self._parsed: bool = False


	def includes(self) -> List[str]:
		if self._includes:
			return self._includes

		self.parse()
		assert isinstance(self._includes, list)
		return self._includes


	def content(self) -> str:
		if self._content:
			return self._content

		self.parse()
		assert isinstance(self._content, str)
		return self._content


	cache = {}
	@classmethod
	def get_DPP(cls, path, name = ""):
		cache_key = path
		if cache_key in cls.cache:
			return cls.cache[cache_key]

		new_DPP = cls(path, name)
		cls.cache[cache_key] = new_DPP
		return new_DPP


	# // C++ comment.
	single_line_comment_pattern = re.compile(
		r'//.*?\n'
	)
	# /* C comment. */
	multi_line_comment_pattern = re.compile(
		r'/\*.*?\*/', re.S
	)
	# "complex \"stri\\\ng\" value".
	string_pattern = re.compile(
		r'[^\']".*?(?<=[^\\])"', re.S
	)
	# #include <something>
	include_pattern = re.compile(
		r'[\n\s]*#\s*include\s*(<|")(?P<path>.*?)("|>)', re.S
	)
	# #pragma once
	pragma_once_pattern = re.compile(
		r'[\n\s]*#\s*pragma\s+once[\n]*', re.S
	)


	# Returns True if the match is within list of other matches
	def _is_within(self, match, matches):
		for m in matches:
			if m.start() <= match.start() and match.end() <= m.end():
				return True
		return False


	def parse(self) -> None:
		if self._parsed:
			return

		if g_verbose:
			print(f"  parsing {self.path}...")

		# Find contexts in the content in which a found include
		# directive should not be processed.
		skippable = []

		raw_content = open(self.path).read()
		i, max_i = 1, len(raw_content)
		while i < max_i:
			cur_char = raw_content[i]
			prev_char = raw_content[i - 1]

			if cur_char == '"':
				match = self.string_pattern.search(raw_content, i - 1)
				if match:
					skippable.append(match)
					i = match.end() - 1

			elif cur_char == '*' and prev_char == '/':
				match = self.multi_line_comment_pattern.search(raw_content, i - 1)
				if match:
					skippable.append(match)
					i = match.end() - 1

			elif cur_char == '/' and prev_char == '/':
				match = self.single_line_comment_pattern.search(raw_content, i - 1)
				if match:
					skippable.append(match)
					i = match.end() - 1

			i += 1

		self._content = ""
		self._includes = []

		pragma_include = re.compile(self.pragma_once_pattern.pattern + "|" + self.include_pattern.pattern)

		i = 0
		for match in pragma_include.finditer(raw_content):
			if self._is_within(match, skippable):
				continue

			if self.include_pattern.match(match.group(0)):
				self._includes.append(''.join(match.group(j) for j in range(1, 4)))

			l, r = match.span()
			self._content += raw_content[i : l]
			i = r

		self._content += raw_content[i :]
		self._parsed = True

		if g_verbose:
			print(f"    found dependencies: {self._includes}")
			print("  ... done parsing file\n")



class Amalgamation(object):
	def __init__(
		self, root_dir: str, source_file: str, target_file: str,
		include_paths: List[str], no_expand: List[str], verbose
	) -> None:
		self.root_dir = os.path.abspath(root_dir);
		self.source_file = source_file if os.path.isabs(source_file) else os.path.join(self.root_dir, source_file)
		self.target_file = target_file if os.path.isabs(target_file) else os.path.join(self.root_dir, target_file)
		self.include_paths = [i if os.path.isabs(i) else os.path.join(self.root_dir, i) for i in include_paths]
		self.no_expand = [i if i[0] == '"' else '"' + i + '"' for i in no_expand]
		global g_verbose
		g_verbose = verbose

		self.DPP = DPP.get_DPP(self.source_file, os.path.basename(self.source_file))

		self._generated_dependency_tree: bool = False
		self._no_expand_deps: List[str] = []
		self._deps: List[DPP] = []

		if g_verbose:
			print("  root_dir", self.root_dir)
			print("  source_file", self.source_file)
			print("  target_file", self.target_file)
			print("  include_paths", self.include_paths)
			print("  no_expand", self.no_expand)
			print("  verbose", g_verbose)
			print("")


	def no_expand_deps(self):
		self._generate_dependency_tree()
		return self._no_expand_deps


	def deps(self):
		self._generate_dependency_tree()
		return self._deps


	def _generate_dependency_tree(self):
		if self._generated_dependency_tree:
			return

		vis = {}

		def dfs(u: DPP) -> None:
			for v_include in u.includes():
				if v_include in vis:
					continue

				if v_include[0] == '<' or v_include in self.no_expand:
					self._no_expand_deps.append(v_include)
					vis[v_include] = True
					continue

				v_path = os.path.join(os.path.dirname(u.path), v_include[1 : -1])
				if not os.path.isfile(v_path):
					for i_p in self.include_paths:
						candi = os.path.join(self.root_dir, i_p, v_include[1 : -1])
						if os.path.isfile(candi):
							v_path = candi

				v = DPP.get_DPP(v_path, os.path.basename(v_path))
				if v_path in vis:
					continue

				vis[v_path] = True
				dfs(v)

			self._deps.append(u)

		dfs(self.DPP)
		self._generated_dependency_tree = True


	def dump(self):
		amalgamation = "#pragma once\n// " + os.path.basename(self.target_file) + " amalgamation\n\n"

		stl, no_stl = [], []
		for dep in self.no_expand_deps():
			if dep[0] == '<':
				stl.append(dep)
			else:
				no_stl.append(dep)

		if g_verbose:
			print("  processing amalgamation...")

		stl.sort()
		for dep in stl:
			amalgamation += "#include " + dep + "\n"
		if len(stl) > 0:
			amalgamation += "\n"
		no_stl.sort()
		for dep in no_stl:
			amalgamation += "#include " + dep + "\n"

		for dep in self.deps():
			amalgamation += "\n// " + dep.name + "\n" + dep.content()

		open(self.target_file, 'w').write(amalgamation)

		if g_verbose:
			print("  ... done!")



def main():
	argparser = argparse.ArgumentParser(
        description = "Amalgamation: reduce file and dependency complexity.",
		usage = "\n".join([
			"    amalgamation",
			"    [--root, -R]       set root directory (default .)",
			"    --source, -S       set source file",
			"    --target, -T       set target file",
			"    [--include, -I]    add include path",
			"    [--no-expand, -N]  skip amalgamation for a file",
			"    [--verbose, -v]    set verbosity (default disabled)"
		])
	)

	argparser.add_argument(
		"-R", "--root",
		dest="root_dir",
		default=".",
		metavar="root/dir",
		help="set root directory",
	)
	argparser.add_argument(
		"-S", "--source",
		dest="source_file",
		required=True,
		metavar="path/to/source",
		help="set source file",
	)
	argparser.add_argument(
		"-T", "--target",
		dest="target_file",
		required=True,
		metavar="path/to/target",
		help="set target file",
	)
	argparser.add_argument(
		"-I", "--include",
		dest="include_paths",
		default=[],
		metavar="include/path",
		help="add include path",
		action="append"
	)
	argparser.add_argument(
		"-N", "--no-expand",
		dest="no_expand",
		default=[],
		metavar="[<include> | \"include\"]",
		help="blacklist from amalgamation",
		action="append"
	)
	argparser.add_argument(
		"-v", "--verbose",
		dest="verbose",
		help="enable verbosity",
		action="store_true"
	)

	args = argparser.parse_args()

	amalgamation = Amalgamation(args.root_dir, args.source_file, args.target_file, args.include_paths, args.no_expand, args.verbose)
	amalgamation.dump()



if __name__ == "__main__":
	main()
