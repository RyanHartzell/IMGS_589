#include <iostream>
using namespace std;
class someClass
{
public:
	void setVariable();
	int getVariable();
private:
	int variable;
};

void someClass::setVariable()
{
	variable = 15;
}
int someClass::getVariable()
{
	return variable;
}
class otherClass : public someClass{};
	

int main (void) {
	someClass hello;
	otherClass nollo;
	nollo.setVariable();
	hello.setVariable();

	cout << nollo.getVariable() << endl;
	cout << hello.getVariable() << endl;

	return 0;
}