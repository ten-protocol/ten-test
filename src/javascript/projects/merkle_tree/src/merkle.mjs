import { StandardMerkleTree } from "@openzeppelin/merkle-tree";
import { Command } from 'commander';
import fs from 'fs';

const program = new Command();

program
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--dump_file <value>', 'Input file containing the leafs')
  .option('--leaf_for_proof <value>', 'The leaf used for the proof')
  .parse(process.argv)

  const options = program.opts()

  fs.readFile(options.dump_file, 'utf8', (err, data) => {
        if (err) {
            console.error(err);
            return;
        }
        const rows = data.split(/\r?\n/).filter(row => row.trim() !== '');
        const result = rows.map(row => row.split(','));

        const tree = StandardMerkleTree.of(result, ["string", "bytes32"]);
        console.log('Root:', tree.root);

        const proof = tree.getProof(options.leaf_for_proof.split(','));
        console.log('Proof:', proof[0]);
    });