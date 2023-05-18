{
  outputs = { self, nixpkgs }: {
    packages."x86_64-linux".default =
      with (import nixpkgs { system = "x86_64-linux"; });
      let
        pythonWithPkgs = python3.withPackages (ps: [ ps.flask ]);
      in
      writeShellScriptBin "app" ''
        export PATH="$PATH:${nasm}/bin"
        exec ${pythonWithPkgs}/bin/python ./app.py
      '';
  };
}
