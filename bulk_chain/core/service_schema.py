class SchemaService(object):

    def __init__(self, json_data):
        self.src = json_data
        self.name = self.src["name"]
        self.r2p, self.p2r, self.cot_args, self.chain = SchemaService.__init_schema(prompts=json_data["schema"])

    @classmethod
    def from_prompt(cls, prompt):
        prompt_schema = {"name": "prompt", "schema": [{"prompt": prompt, "out": "response", "in": "prompt"}]}
        return cls(prompt_schema)

    @staticmethod
    def __init_schema(prompts):

        schema_args = {}
        schema_r2p = {}
        schema_p2r = {}
        chain = []

        for prompt in prompts:
            r_col_name = prompt["out"]
            p_col_name = r_col_name + "_prompt" if "in" not in prompt else prompt["in"]

            assert r_col_name not in schema_r2p, f"`{r_col_name}` has been already declared!"
            assert p_col_name not in schema_p2r, f"`{p_col_name}` has been already declared!"

            schema_r2p[r_col_name] = p_col_name
            schema_p2r[p_col_name] = r_col_name
            schema_args[p_col_name] = prompt
            schema_args[r_col_name] = None
            chain.append(prompt)

        return schema_r2p, schema_p2r, schema_args, chain
