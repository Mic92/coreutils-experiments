with import <nixpkgs> {};

let
  clang = clang_34.overrideDerivation (old: {
    buildInputs = old.buildInputs ++ [ makeWrapper ];
    buildCommand = old.buildCommand + ''
      wrapProgram "$out/bin/clang" --set hardeningDisable all
      wrapProgram "$out/bin/clang++" --set hardeningDisable all
      ln -s $out/bin/clang $out/bin/clang-3.4
    '';
  });
in stdenv.mkDerivation {
  name = "env";
  buildInputs = [
    bashInteractive
    cmake
    llvm_34
    ninja
    wllvm
    clang
    (python3.withPackages (packages: with packages; [ pandas seaborn flake8 ]))
  ];
}
