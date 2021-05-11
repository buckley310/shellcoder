{
  inputs.nixpkgs.url = "nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }: {
    defaultApp."x86_64-linux" =
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
