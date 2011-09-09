from constants import *

LAMBDA = TT(-1, "<LAMBDA>")

FIRST_block = [BRACE_OPEN]
FIRST_boolean_literal = [TRUE, FALSE]
FIRST_boolean_type = [BOOLEAN_TYPE]
FIRST_class_body = [BRACE_OPEN]
FIRST_class_declaration = [PUBLIC]
FIRST_class_instance_creation = [NEW]
FIRST_constructor_body = [BRACE_OPEN]
FIRST_constructor_declaration = [PUBLIC, PROTECTED]
FIRST_constructor_declarator = [PAREN_OPEN]
FIRST_declarators = [IDENTIFIER]
FIRST_empty_statement = [SCOLON]
FIRST_explicit_constructor_invocation = [SUPER, THIS]
FIRST_field_modifier = [PUBLIC, PROTECTED, STATIC]
FIRST_if_start_statement = [IF]
FIRST_integral_type = [INT_TYPE, CHAR_TYPE]
FIRST_literal = [INT_LITERAL, CHAR_LITERAL, STRING_LITERAL, NULL] + FIRST_boolean_literal
FIRST_method_modifier = [PUBLIC, PROTECTED, STATIC]
FIRST_method_declarator = [IDENTIFIER]
FIRST_primary = [INT_LITERAL] + FIRST_boolean_type + [CHAR_LITERAL, STRING_LITERAL, NULL, THIS, PAREN_OPEN, NEW, SUPER]
FIRST_rest_additive_expression = [ADD, SUB]
FIRST_rest_argument_list = [LAMBDA, COMMA]
FIRST_rest_conditional_and_expression = [LAMBDA, CONDITIONAL_AND]
FIRST_rest_declarators = [COMMA, ASSIGNMENT, PAREN_OPEN, SCOLON]
FIRST_rest_equality_expression = [EQUALS, NOT_EQUALS, LAMBDA]
FIRST_rest_formal_parameter_list = [LAMBDA, COMMA]
FIRST_rest_if_start_statement = [LAMBDA, ELSE]
FIRST_rest_multiplicative_expression = [MUL, DIV, MOD]
FIRST_rest_primary = [ACCESSOR, LAMBDA]
FIRST_rest_relational_expression = [LT, GT, LT_EQ, GT_EQ]
FIRST_rest_variable_declarator = [LAMBDA, ASSIGNMENT]
FIRST_return_statement = [RETURN]
FIRST_variable_declarator = FIRST_rest_variable_declarator
FIRST_rest_variable_declarators = FIRST_variable_declarator
FIRST_while_statement = [WHILE]
FIRST_type_declarations = [LAMBDA] + FIRST_class_declaration

FIRST_numeric_type = FIRST_integral_type
FIRST_primitive_type = [BOOLEAN_TYPE] + FIRST_numeric_type
FIRST_type = [IDENTIFIER] + FIRST_primitive_type

FIRST_postfix_expression = [IDENTIFIER] + FIRST_primary
FIRST_unary_expression_not_plus_minus = [NOT] + FIRST_postfix_expression
FIRST_unary_expression = [ADD, SUB] + FIRST_unary_expression_not_plus_minus
FIRST_multiplicative_expression = FIRST_unary_expression
FIRST_additive_expression = FIRST_multiplicative_expression
FIRST_relational_expression = FIRST_additive_expression
FIRST_equality_expression = FIRST_relational_expression
FIRST_conditional_and_expression = FIRST_equality_expression
FIRST_conditional_or_expression = FIRST_conditional_and_expression
FIRST_conditional_expression = FIRST_conditional_or_expression
FIRST_assignment_expression = FIRST_conditional_expression
FIRST_expression = FIRST_assignment_expression
FIRST_local_variable_declaration = FIRST_type
FIRST_local_variable_declaration_statement = FIRST_local_variable_declaration
FIRST_method_invocation = [IDENTIFIER] + FIRST_primary
FIRST_statement_expression = FIRST_method_invocation
FIRST_expression_statement = FIRST_statement_expression
FIRST_statement_without_trailing_substatements = FIRST_block + FIRST_empty_statement + FIRST_return_statement + FIRST_expression_statement
FIRST_statement = FIRST_while_statement + FIRST_if_start_statement + FIRST_statement_without_trailing_substatements

FIRST_argument_list = FIRST_expression
FIRST_block_statement = FIRST_primitive_type + [IDENTIFIER] + FIRST_if_start_statement + FIRST_while_statement + FIRST_block + FIRST_empty_statement + FIRST_return_statement + FIRST_primary
FIRST_block_statements = FIRST_block_statement
FIRST_field_modifiers = FIRST_field_modifier
FIRST_class_body_declaration = FIRST_field_modifiers
FIRST_class_body_declarations = [LAMBDA] + FIRST_class_body_declaration
FIRST_compilation_unit = FIRST_type_declarations
FIRST_field_access = [SUPER, INT_LITERAL] + FIRST_boolean_literal + [CHAR_LITERAL, STRING_LITERAL, NULL, THIS, PAREN_OPEN,NEW]
FIRST_formal_parameter = FIRST_type
FIRST_formal_parameter_list = FIRST_formal_parameter
FIRST_method_body = FIRST_block
FIRST_method_modifiers = FIRST_method_modifier
FIRST_method_header = FIRST_method_modifiers
FIRST_method_declaration = FIRST_method_header
FIRST_rest2_constructor_body = [BRACE_CLOSE] + FIRST_block_statements
FIRST_rest2_primary = [PAREN_CLOSE] + FIRST_argument_list
FIRST_rest_block = [BRACE_CLOSE] + FIRST_block_statements
FIRST_rest_class_body = [BRACE_CLOSE] + FIRST_class_body_declarations
FIRST_rest_class_declaration = [EXTENDS] + FIRST_class_body
FIRST_rest_constructor_body = [BRACE_CLOSE] + FIRST_block_statements + FIRST_explicit_constructor_invocation
FIRST_rest_explicit_constructor_invocation = [PAREN_CLOSE] + FIRST_argument_list
FIRST_rest_field_modifiers = [LAMBDA] + FIRST_field_modifiers
FIRST_rest_method_invocation = [PAREN_CLOSE] + FIRST_argument_list
FIRST_rest_return_statement = [SCOLON] + FIRST_expression
