{
 description = "Python development environment";

 inputs.nixpkgs.url = "github:nixos/nixpkgs";

 outputs = { self, nixpkgs }:
   let
     system = "x86_64-linux";
     pkgs = import nixpkgs { inherit system; };
     python = pkgs.python312.withPackages (ps: with ps; [
       qrcode
       aiohttp
       ping3
       requests
       discordpy
     ]);
   in
   {
     devShells.${system}.default = pkgs.mkShell {
       buildInputs = [ python ];
     };
   };
}